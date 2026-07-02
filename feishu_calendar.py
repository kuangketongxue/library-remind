"""
飞书日程集成模块
- 后台 QThread 调用 lark-cli calendar +agenda
- 解析 JSON 结果，提供「当前日程」「下一日程」查询
- 5 分钟缓存，避免频繁子进程调用
"""
import json
import logging
import os
import shutil
import subprocess
import traceback
from datetime import datetime, timedelta, timezone

from PyQt5.QtCore import QThread, pyqtSignal, QTimer

log = logging.getLogger('rest_reminder')


def _find_lark_cli():
    """查找 lark-cli 可执行文件的完整路径（pythonw 环境下 PATH 可能不完整）"""
    # 1. 先试 shutil.which（能在 PATH 中找到就用）
    path = shutil.which('lark-cli')
    if path:
        return path
    # 2. Windows 上 .cmd 文件需要显式指定
    path = shutil.which('lark-cli.cmd')
    if path:
        return path
    # 3. 搜索常见安装位置
    candidates = [
        os.path.expandvars(r'%APPDATA%\npm\lark-cli.cmd'),
        os.path.expandvars(r'%LOCALAPPDATA%\npm\lark-cli.cmd'),
        r'C:\Program Files\nodejs\lark-cli.cmd',
        os.path.expanduser('~/.local/bin/lark-cli'),
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    return 'lark-cli'  # fallback，让 subprocess 报错

_TZ_CST = timezone(timedelta(hours=8))


def _parse_iso(s):
    """解析 ISO 8601 时间字符串为 datetime（带时区）"""
    if not s:
        return None
    try:
        return datetime.fromisoformat(s)
    except (ValueError, TypeError):
        return None


def _fmt_time(dt):
    """格式化 datetime 为 HH:MM"""
    if dt is None:
        return '--:--'
    return dt.strftime('%H:%M')


def _fmt_duration(start, end):
    """格式化时长，如 '30分钟' / '1.5小时'"""
    if not start or not end:
        return ''
    mins = (end - start).total_seconds() / 60
    if mins < 60:
        return f'{int(mins)}分钟'
    hours = mins / 60
    if hours == int(hours):
        return f'{int(hours)}小时'
    return f'{hours:.1f}小时'


class CalendarEvent:
    """单个日程事件的轻量数据类"""
    __slots__ = ('summary', 'description', 'start', 'end', 'event_id',
                 'is_all_day', 'meeting_url', 'rsvp_status')

    def __init__(self, summary, description, start, end, event_id,
                 is_all_day=False, meeting_url='', rsvp_status=''):
        self.summary = summary
        self.description = description
        self.start = start
        self.end = end
        self.event_id = event_id
        self.is_all_day = is_all_day
        self.meeting_url = meeting_url
        self.rsvp_status = rsvp_status

    @property
    def time_range(self):
        if self.is_all_day:
            return '全天'
        return f'{_fmt_time(self.start)} - {_fmt_time(self.end)}'

    @property
    def duration_text(self):
        if self.is_all_day:
            return '全天'
        return _fmt_duration(self.start, self.end)

    def status_at(self, now):
        """返回该事件在 now 时刻的状态：ongoing / upcoming / ended"""
        if self.is_all_day:
            if self.start and self.end:
                if self.start.date() <= now.date() <= self.end.date():
                    return 'ongoing'
                elif now.date() < self.start.date():
                    return 'upcoming'
            return 'ended'
        if self.start and self.end:
            if self.start <= now <= self.end:
                return 'ongoing'
            elif now < self.start:
                return 'upcoming'
        return 'ended'

    def minutes_until_start(self, now):
        """距离开始还有多少分钟（已开始则返回负数）"""
        if not self.start:
            return float('inf')
        return (self.start - now).total_seconds() / 60

    def minutes_until_end(self, now):
        """距离结束还有多少分钟"""
        if not self.end:
            return float('inf')
        return (self.end - now).total_seconds() / 60


class _FetchWorker(QThread):
    """后台线程：执行 lark-cli 并返回解析后的事件列表"""
    fetched = pyqtSignal(list)      # 成功时发送 [CalendarEvent, ...]
    error = pyqtSignal(str)         # 失败时发送错误信息

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cancelled = False

    def cancel(self):
        self._cancelled = True

    def run(self):
        if self._cancelled:
            return
        try:
            now = datetime.now(_TZ_CST)
            # 查询今天 + 明天（确保能拿到"下一日程"）
            start_str = now.strftime('%Y-%m-%d')
            tomorrow = now + timedelta(days=1)
            end_str = tomorrow.strftime('%Y-%m-%d')

            cli_path = _find_lark_cli()
            cmd = [
                cli_path, 'calendar', '+agenda',
                '--as', 'user',
                '--start', start_str,
                '--end', end_str,
                '--format', 'json',
            ]

            # 最多重试 2 次（应对 token 刷新窗口/网络瞬断）
            last_err = ''
            for attempt in range(2):
                if self._cancelled:
                    return
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        encoding='utf-8',
                        timeout=30,
                        creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0,
                    )
                except subprocess.TimeoutExpired:
                    last_err = 'lark-cli 超时（30秒）'
                    if attempt == 0:
                        import time as _time
                        _time.sleep(2)
                        continue
                    self.error.emit(last_err)
                    return

                if self._cancelled:
                    return

                # returncode != 0 时，仍尝试解析 stdout（lark-cli 有时 returncode=1 但 stdout 有 JSON）
                stdout = result.stdout or ''
                stderr = result.stderr or ''

                if result.returncode != 0:
                    # 先试 stdout 是否有有效 JSON
                    parsed = None
                    if stdout.strip():
                        try:
                            parsed = json.loads(stdout)
                        except (json.JSONDecodeError, ValueError):
                            pass
                    if parsed is not None and parsed.get('ok'):
                        data = parsed
                    else:
                        # 真正失败，记录 stdout + stderr（消除诊断盲区）
                        last_err = f'lark-cli 返回 {result.returncode}: stdout={stdout[:200]} stderr={stderr[:200]}'
                        if attempt == 0:
                            import time as _time
                            _time.sleep(2)
                            continue
                        self.error.emit(last_err)
                        return
                else:
                    # returncode=0，解析 stdout
                    if not stdout.strip():
                        # stdout 为空（lark-cli 异常退出但 returncode=0）
                        last_err = 'lark-cli 返回 0 但 stdout 为空'
                        if attempt == 0:
                            import time as _time
                            _time.sleep(2)
                            continue
                        self.error.emit(last_err)
                        return
                    try:
                        data = json.loads(stdout)
                    except (json.JSONDecodeError, ValueError) as e:
                        last_err = f'JSON 解析失败: {e} (stdout={stdout[:100]})'
                        if attempt == 0:
                            import time as _time
                            _time.sleep(2)
                            continue
                        self.error.emit(last_err)
                        return

                if not data.get('ok'):
                    err_msg = data.get('error', {}).get('message', '未知错误')
                    last_err = f'飞书 API 错误: {err_msg}'
                    if attempt == 0:
                        import time as _time
                        _time.sleep(2)
                        continue
                    self.error.emit(last_err)
                    return

                # 成功，跳出重试循环
                break
            else:
                # 两次都失败
                self.error.emit(last_err or '获取失败（重试 2 次均失败）')
                return

            events = []
            for item in data.get('data', []):
                start_dt = _parse_iso(item.get('start_time', {}).get('datetime'))
                end_dt = _parse_iso(item.get('end_time', {}).get('datetime'))
                # 检测全天事件（start/end 仅有日期部分）
                is_all_day = False
                if start_dt and end_dt:
                    raw_start = item.get('start_time', {}).get('datetime', '')
                    if 'T' not in raw_start:
                        is_all_day = True

                vchat = item.get('vchat') or {}
                meeting_url = vchat.get('meeting_url', '')

                evt = CalendarEvent(
                    summary=item.get('summary', '(无标题)'),
                    description=item.get('description', ''),
                    start=start_dt,
                    end=end_dt,
                    event_id=item.get('event_id', ''),
                    is_all_day=is_all_day,
                    meeting_url=meeting_url,
                    rsvp_status=item.get('self_rsvp_status', ''),
                )
                events.append(evt)

            # 按开始时间排序
            events.sort(key=lambda e: e.start or datetime.min.replace(tzinfo=_TZ_CST))

            if not self._cancelled:
                self.fetched.emit(events)

        except FileNotFoundError:
            self.error.emit('未找到 lark-cli，请确认已安装')
        except Exception as e:
            self.error.emit(f'{type(e).__name__}: {e}')
            log.error(f'[FeishuCalendar] 后台获取失败: {traceback.format_exc()}')


class FeishuCalendarManager:
    """
    日程管理器（主线程使用）

    用法：
        mgr = FeishuCalendarManager()
        mgr.start()                    # 启动后台获取
        current = mgr.get_current()    # 当前进行中的日程
        upcoming = mgr.get_upcoming()  # 下一个即将开始的日程
        all_events = mgr.get_today_events()  # 今日全部日程
    """

    def __init__(self, refresh_interval=86400):
        """
        Args:
            refresh_interval: 自动刷新间隔（秒），默认 24 小时（每天获取一次）
        """
        self._events = []
        self._last_fetch = None
        self._error_msg = ''
        self._worker = None
        self._refresh_interval = refresh_interval
        self._enabled = True
        self._fetch_count = 0
        self._retry_count = 0  # 失败重试计数
        self._max_retries = 3  # 最多重试 3 次

        # 定时刷新器
        self._refresh_timer = QTimer()
        self._refresh_timer.timeout.connect(self._auto_refresh)
        # 失败重试定时器
        self._retry_timer = QTimer()
        self._retry_timer.setSingleShot(True)
        self._retry_timer.timeout.connect(self._do_retry)

    @property
    def enabled(self):
        return self._enabled

    @enabled.setter
    def enabled(self, val):
        self._enabled = bool(val)
        if self._enabled:
            self.refresh()
            self._refresh_timer.start(self._refresh_interval * 1000)
        else:
            self._refresh_timer.stop()
            self._events.clear()

    @property
    def error_message(self):
        return self._error_msg

    @property
    def last_fetch_time(self):
        return self._last_fetch

    @property
    def fetch_count(self):
        return self._fetch_count

    def start(self):
        """启动管理器：立即获取一次 + 开启定时刷新"""
        if not self._enabled:
            return
        self.refresh()
        self._refresh_timer.start(self._refresh_interval * 1000)

    def stop(self):
        """停止管理器：取消后台任务 + 停止定时器"""
        self._refresh_timer.stop()
        self._retry_timer.stop()
        if self._worker and self._worker.isRunning():
            self._worker.cancel()
            self._worker.wait(3000)

    def refresh(self):
        """手动触发一次后台获取"""
        if not self._enabled:
            return
        if self._worker and self._worker.isRunning():
            return
        self._worker = _FetchWorker()
        self._worker.fetched.connect(self._on_fetched)
        self._worker.error.connect(self._on_error)
        self._worker.start()

    def _auto_refresh(self):
        """定时器回调"""
        self.refresh()

    def _on_fetched(self, events):
        """后台线程成功回调（主线程执行）"""
        self._events = events
        self._last_fetch = datetime.now()
        self._error_msg = ''
        self._fetch_count += 1
        self._retry_count = 0  # 成功则重置重试计数
        self._retry_timer.stop()  # 停止重试定时器
        log.info(f'[FeishuCalendar] 获取成功，{len(events)} 个日程')

    def _on_error(self, msg):
        """后台线程失败回调（主线程执行）"""
        self._error_msg = msg
        log.warning(f'[FeishuCalendar] 获取失败: {msg}')
        # 失败重试：最多 3 次，每次间隔 10 分钟
        if self._retry_count < self._max_retries:
            self._retry_count += 1
            wait_min = 10
            log.info(f'[FeishuCalendar] 将在 {wait_min} 分钟后重试（第 {self._retry_count}/{self._max_retries} 次）')
            self._retry_timer.start(wait_min * 60 * 1000)
        else:
            log.warning(f'[FeishuCalendar] 已达最大重试次数 {self._max_retries}，停止重试')

    def _do_retry(self):
        """失败后重试"""
        log.info(f'[FeishuCalendar] 重试第 {self._retry_count}/{self._max_retries} 次')
        self.refresh()

    # ─── 查询接口 ───

    def get_today_events(self):
        """获取今日全部日程（已按时间排序）"""
        now = datetime.now(_TZ_CST)
        today = now.date()
        result = []
        for evt in self._events:
            if evt.is_all_day:
                if evt.start and evt.start.date() <= today <= (evt.end or evt.start).date():
                    result.append(evt)
            elif evt.start and evt.start.date() == today:
                result.append(evt)
        return result

    def get_current(self):
        """
        获取当前正在进行的日程。
        返回 CalendarEvent 或 None。
        """
        now = datetime.now(_TZ_CST)
        for evt in self._events:
            if evt.status_at(now) == 'ongoing':
                return evt
        return None

    def get_upcoming(self, within_minutes=1440):
        """
        获取下一个即将开始的日程。
        Args:
            within_minutes: 只返回在此分钟内即将开始的事件
        返回 CalendarEvent 或 None。
        """
        now = datetime.now(_TZ_CST)
        best = None
        for evt in self._events:
            status = evt.status_at(now)
            if status == 'upcoming':
                mins = evt.minutes_until_start(now)
                if 0 <= mins <= within_minutes:
                    if best is None or evt.start < best.start:
                        best = evt
        return best

    def get_current_and_next(self):
        """
        返回 (current_event, next_event) 元组。
        可能都是 None。
        """
        return self.get_current(), self.get_upcoming()

    def get_last_sync_status(self):
        """获取最近一次同步状态"""
        if not self._last_fetch:
            return {'last_success': '从未', 'last_error': '', 'retry_count': 0}
        last_success = self._last_fetch.strftime('%Y-%m-%d %H:%M')
        last_error = self._error_msg or ''
        retry_count = self._retry_count
        return {
            'last_success': last_success,
            'last_error': last_error,
            'retry_count': retry_count,
        }

    def get_display_text(self, short=False):
        """
        生成适合 UI 展示的日程摘要文本。
        short=True: 仅返回 "summary time_range" 格式（用于 popup 等窄空间）
        返回格式如：
          - "▶ 正在开会（14:00-15:00）"
          - "⏳ 下一个：产品评审（16:00-17:00，还有45分钟）"
          - "📅 今日无日程"
        """
        current, upcoming = self.get_current_and_next()

        if current:
            if short:
                return f'{current.summary} {current.time_range}'
            remaining = current.minutes_until_end(datetime.now(_TZ_CST))
            remaining_text = ''
            if remaining > 0:
                if remaining < 60:
                    remaining_text = f'，还有{int(remaining)}分钟结束'
                else:
                    remaining_text = f'，还有{remaining/60:.1f}小时结束'
            return f'▶ {current.summary}（{current.time_range}{remaining_text}）'

        if upcoming:
            if short:
                return f'{upcoming.summary} {upcoming.time_range}'
            now = datetime.now(_TZ_CST)
            mins = upcoming.minutes_until_start(now)
            soon_text = ''
            if mins < 60:
                soon_text = f'，{int(mins)}分钟后开始'
            elif mins < 1440:
                hours = mins / 60
                soon_text = f'，{hours:.1f}小时后开始'
            return f'⏳ {upcoming.summary}（{upcoming.time_range}{soon_text}）'

        if self._error_msg:
            return f'⚠️ 日程获取失败'

        return '📅 今日无日程'
