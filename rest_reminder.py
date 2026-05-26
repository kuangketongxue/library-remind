"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
- 监控电池充电状态
- 监控电脑使用时长（每 3 小时提醒）
- 学习时长本地计数（每次倒计时完成算 1 小时）
"""
import sys
import time
import random
import requests
import ctypes
import json
import os
import subprocess
import tempfile
import re
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon, QFont, QCursor, QPainter, QColor, QBrush, QPen
import psutil
import atexit
import winreg
import traceback
import winsound
import math
import logging
from logging.handlers import RotatingFileHandler

# 日志配置：写入文件（pythonw 模式下 print 全部丢失），自动轮转 3×1MB
_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest_reminder.log')
_handler = RotatingFileHandler(_LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
log = logging.getLogger('rest_reminder')
log.setLevel(logging.INFO)
log.addHandler(_handler)


def open_url(url):
    """使用 Windows API 打开 URL，避免弹出命令窗口"""
    if not url.startswith('https://'):
        log.error(f'[open_url] 拒绝非 HTTPS URL: {url[:50]}')
        return False
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None,
            'open',
            url,
            None,
            None,
            1  # SW_SHOWNORMAL
        )
        return True
    except Exception as e:
        log.error(f'[open_url] 使用 ShellExecuteW 失败: {e}')
        try:
            import webbrowser
            return webbrowser.open(url)
        except Exception as e2:
            log.error(f'[open_url] 使用 webbrowser 也失败: {e2}')
            return False


class FloatingBall(QWidget):
    """小浮球，点击显示/隐藏主窗口"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dragging = False
        self.drag_position = None
        self.click_time = None

        self.setWindowFlags(
            Qt.WindowStaysOnTopHint |
            Qt.FramelessWindowHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)

        # 初始位置：屏幕右侧中间
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.geometry()
            self.move(screen_geom.width() - 80, screen_geom.height() // 2 - 30)

        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 绘制圆形背景
        color = QColor(120, 140, 87)  # 绿色，与按钮颜色一致
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(0, 0, 60, 60)

        # 绘制图标文字
        painter.setPen(QColor(250, 249, 245))
        painter.setFont(QFont('Arial', 20, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, '⏰')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.click_time = datetime.now()

    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            # 如果拖动距离很小，认为是点击
            delta = (datetime.now() - self.click_time).total_seconds()
            if delta < 0.3:
                if self.main_window.isVisible():
                    self.main_window.hide()
                else:
                    self.main_window.show()
                    self.main_window.activateWindow()
                    self.main_window.raise_()


# 飞书多维表格配置（必须通过环境变量设置，开源版本不包含默认值）
FEISHU_BASE_TOKEN = os.environ.get('FEISHU_BASE_TOKEN')
FEISHU_TABLE_ID = os.environ.get('FEISHU_TABLE_ID')

if not FEISHU_BASE_TOKEN or not FEISHU_TABLE_ID:
    log.warning('未设置飞书同步凭据（FEISHU_BASE_TOKEN / FEISHU_TABLE_ID），飞书同步功能将禁用')
    FEISHU_BASE_TOKEN = FEISHU_BASE_TOKEN or ''
    FEISHU_TABLE_ID = FEISHU_TABLE_ID or ''


class FeishuSync:
    """通过 lark-cli 将学习/电脑使用时长同步到飞书多维表格"""

    _record_id = None
    _current_date = None

    @classmethod
    def _get_cache_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.feishu_cache.json')

    @classmethod
    def _load_cache(cls):
        path = cls._get_cache_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}

    @classmethod
    def _save_cache(cls, date, record_id):
        with open(cls._get_cache_path(), 'w', encoding='utf-8') as f:
            json.dump({'date': date, 'record_id': record_id}, f, ensure_ascii=False)

    @classmethod
    def _call_lark(cls, args, data=None):
        """调用 lark-cli，返回解析后的 JSON"""
        # Windows: lark-cli 是 .cmd 批处理 shim，必须 shell=True 才能执行
        is_windows = sys.platform == 'win32'
        cmd_args = ['lark-cli'] + list(args)
        tmp = None
        if data:
            tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.feishu_tmp.json')
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)
            # Windows 下 shell=True 用 list2cmdline 拼接，确保 @file 引用正确
            cmd_args += ['--json', '@' + tmp]
        try:
            # shell=True 是 windows .cmd shim 的关键修复
            # Windows pipe 的 GBK 编码问题：必须二进制捕获然后手动 utf-8 decode，
            # 不能用 text=True + encoding='utf-8'（内部线程仍会用 gbk 解码导致 UnicodeDecodeError）
            result = subprocess.run(
                cmd_args, capture_output=True, timeout=30,
                cwd=os.path.dirname(os.path.abspath(__file__)),
                shell=is_windows
            )
            stdout = result.stdout.decode('utf-8', errors='replace')
            stderr = result.stderr.decode('utf-8', errors='replace') if result.stderr else ''
            if result.returncode != 0:
                redacted = [a if 'token' not in a.lower() else a[:10] + '***' for a in cmd_args]
                log.error(f'[FeishuSync] lark-cli 返回码 {result.returncode}')
                log.error(f'[FeishuSync] 执行命令: {" ".join(redacted)[:200]}')
                if stderr:
                    log.error(f'[FeishuSync] stderr: {stderr[:500]}')
            return json.loads(stdout) if stdout.strip() else {}
        except Exception as e:
            log.error(f'[FeishuSync] lark-cli 调用失败: {e}')
            return {}
        finally:
            if tmp and os.path.exists(tmp):
                os.unlink(tmp)

    @classmethod
    def _find_today_record(cls):
        """分页查询今天是否已有记录，返回 record_id 或 None

        该表可能超过 200 条记录，必须逐页遍历查找今日记录。
        """
        today = datetime.now().date().isoformat()
        offset = 0
        while True:
            resp = cls._call_lark([
                'base', '+record-list',
                '--base-token', FEISHU_BASE_TOKEN,
                '--table-id', FEISHU_TABLE_ID,
                '--as', 'user',
                '--limit', '200',
                '--offset', str(offset),
                '--format', 'json'
            ])
            if not resp.get('ok'):
                log.error(f'[FeishuSync] +record-list 未返回 ok，跳过')
                return None

            d = resp.get('data', {})
            records = d.get('data', [])
            if not records:
                break

            field_ids = d.get('field_id_list', [])
            rids = d.get('record_id_list', [])

            try:
                date_idx = field_ids.index('fldTXDs0Ro')
            except ValueError:
                log.error('[FeishuSync] 找不到日期字段 fldTXDs0Ro')
                return None

            for i, rec in enumerate(records):
                if i >= len(rids):
                    break
                date_val = rec[date_idx] if date_idx < len(rec) else None
                if date_val is None:
                    continue
                if isinstance(date_val, (int, float)):
                    dt = datetime.fromtimestamp(date_val / 1000)
                    date_str = dt.strftime('%Y-%m-%d')
                elif isinstance(date_val, str):
                    date_str = date_val[:10]
                else:
                    continue
                if date_str == today:
                    rid = rids[i]
                    log.info(f'[FeishuSync] 找到今日记录: {rid}')
                    return rid

            # 检查是否有下一页
            has_more = d.get('has_more', False)
            if not has_more:
                break
            offset += len(records)
            if offset >= 2000:
                log.error('[FeishuSync] 翻页超过 2000 条仍未找到今日记录，终止')
                break

        log.info('[FeishuSync] 未找到今天的记录')
        return None

    @classmethod
    def _ensure_record(cls):
        """确保今天的记录存在，返回 record_id"""
        today = datetime.now().date().isoformat()

        # 内存缓存命中
        if cls._record_id and cls._current_date == today:
            return cls._record_id

        # 本地缓存命中
        cache = cls._load_cache()
        if cache.get('date') == today and cache.get('record_id'):
            cls._record_id = cache['record_id']
            cls._current_date = today
            return cls._record_id

        # 查飞书（逐页扫描，确保不漏）
        record_id = cls._find_today_record()
        if record_id:
            cls._record_id = record_id
            cls._current_date = today
            cls._save_cache(today, record_id)
            return record_id

        # 确实没有今天的记录才新建
        log.info('[FeishuSync] 创建新记录')
        resp = cls._call_lark([
            'base', '+record-upsert',
            '--base-token', FEISHU_BASE_TOKEN,
            '--table-id', FEISHU_TABLE_ID,
            '--as', 'user'
        ], {'日期': today, '学习时长（H）': 0, '电脑使用时长（H）': 0})
        if resp.get('ok'):
            rid = resp['data']['record']['record_id_list'][0]
            cls._record_id = rid
            cls._current_date = today
            cls._save_cache(today, rid)
            return rid
        return None

    @classmethod
    def _update_field(cls, field_name, new_value):
        """更新指定字段的值，如果找不到记录则跳过"""
        record_id = cls._ensure_record()
        if not record_id:
            log.error(f'[FeishuSync] 无法获取记录，跳过更新 {field_name}')
            return False

        resp = cls._call_lark([
            'base', '+record-upsert',
            '--base-token', FEISHU_BASE_TOKEN,
            '--table-id', FEISHU_TABLE_ID,
            '--record-id', record_id,
            '--as', 'user'
        ], {field_name: round(new_value, 1)})
        if resp.get('ok'):
            log.info(f'[FeishuSync] 更新成功: {field_name} = {round(new_value, 1)}')
            return True
        else:
            log.error(f'[FeishuSync] 更新失败（可能缓存过期）: {resp}')
            cls.reset()
            new_record_id = cls._ensure_record()
            if new_record_id and new_record_id != record_id:
                resp2 = cls._call_lark([
                    'base', '+record-upsert',
                    '--base-token', FEISHU_BASE_TOKEN,
                    '--table-id', FEISHU_TABLE_ID,
                    '--record-id', new_record_id,
                    '--as', 'user'
                ], {field_name: round(new_value, 1)})
                if resp2.get('ok'):
                    log.info(f'[FeishuSync] 重试更新成功: {field_name} = {round(new_value, 1)}')
                    return True
                else:
                    log.error(f'[FeishuSync] 重试也失败: {resp2}')
            return False

    @classmethod
    def increment_study_hour(cls, total_hours):
        """学习满 1 小时，更新飞书中的学习时长"""
        log.info(f'[FeishuSync] 记录学习时长: {total_hours}h')
        return cls._update_field('学习时长（H）', total_hours)

    @classmethod
    def increment_computer_hour(cls, total_hours):
        """电脑使用满 3 小时，更新飞书中的电脑使用时长"""
        log.info(f'[FeishuSync] 记录电脑使用时长: {total_hours}h')
        return cls._update_field('电脑使用时长（H）', total_hours)

    @classmethod
    def reset(cls):
        """日期切换时重置缓存"""
        cls._record_id = None
        cls._current_date = None


class SingleInstanceChecker:
    """单实例检查器 - 确保程序只运行一个实例"""
    def __init__(self):
        self.lock_file = None
        self.lock_path = os.path.join(tempfile.gettempdir(), 'rest_reminder.lock')
        self.lock_handle = None

    def is_already_running(self):
        try:
            import msvcrt
            try:
                self.lock_handle = open(self.lock_path, 'w')
                msvcrt.locking(self.lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                self.lock_handle.write(str(os.getpid()))
                self.lock_handle.flush()
                self.lock_file = self.lock_path
                atexit.register(self.cleanup)
                return False
            except IOError:
                if self.lock_handle:
                    self.lock_handle.close()
                    self.lock_handle = None
                return True
        except ImportError:
            return self._fallback_check()
        except Exception as e:
            log.error(f'单实例检查失败：{e}')
            return False

    def _fallback_check(self):
        try:
            if os.path.exists(self.lock_path):
                try:
                    with open(self.lock_path, 'r') as f:
                        old_pid = int(f.read().strip())
                    if psutil.pid_exists(old_pid):
                        try:
                            proc = psutil.Process(old_pid)
                            cmdline = ' '.join(proc.cmdline())
                            if 'rest_reminder' in cmdline:
                                return True
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    os.remove(self.lock_path)
                except (ValueError, IOError):
                    try:
                        os.remove(self.lock_path)
                    except:
                        pass
            with open(self.lock_path, 'w') as f:
                f.write(str(os.getpid()))
            self.lock_file = self.lock_path
            atexit.register(self.cleanup)
            return False
        except Exception as e:
            log.error(f'备用单实例检查失败：{e}')
            return False

    def cleanup(self):
        try:
            if self.lock_handle:
                try:
                    import msvcrt
                    msvcrt.locking(self.lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except:
                    pass
                self.lock_handle.close()
                self.lock_handle = None
            if self.lock_file and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass


from PyQt5.QtCore import QThread, pyqtSignal


class CountdownOverlay(QWidget):
    """小型浮窗倒计时：拖动、位置记忆、进度条、呼吸动画、音效"""
    _POS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.overlay_pos.json')

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 110)

        self._drag_offset = None
        self._total_seconds = 300
        self._chimed = False

        self.setStyleSheet("""
            background-color: rgba(30, 30, 30, 210);
            border-radius: 12px;
            border: 1px solid rgba(255, 217, 61, 0.15);
        """)
        self.setCursor(Qt.OpenHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(2)

        self.title_label = QLabel('')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('color: #FFD93D; font-size: 12px; font-weight: bold; background: transparent; border: none;')

        self.timer_label = QLabel('')
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet('color: #FFFFFF; font-size: 36px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')

        self.hint_label = QLabel('')
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet('color: #999; font-size: 11px; background: transparent; border: none;')

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background: rgba(255,255,255,0.06); border: none; border-radius: 2px; }
            QProgressBar::chunk { background: qlineargradient(x1:0, x2:1, stop:0 #788C57, stop:0.6 #FFD93D, stop:1 #FF6B50); border-radius: 2px; }
        """)

        layout.addWidget(self.title_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.progress_bar)

        for w in (self.title_label, self.timer_label, self.hint_label, self.progress_bar):
            w.installEventFilter(self)

        self._load_position()
        self.hide()

    def eventFilter(self, obj, event):
        t = event.type()
        if t == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)
            return True
        if t == QEvent.MouseMove and self._drag_offset is not None:
            self.move(event.globalPos() - self._drag_offset)
            return True
        if t == QEvent.MouseButtonRelease:
            self._drag_offset = None
            self.setCursor(Qt.OpenHandCursor)
            self._save_position()
            return True
        return super().eventFilter(obj, event)

    def _load_position(self):
        try:
            if os.path.exists(self._POS_FILE):
                with open(self._POS_FILE, 'r') as f:
                    pos = json.load(f)
                x, y = pos['x'], pos['y']
                # 校验坐标在当前屏幕范围内
                screen = QApplication.primaryScreen()
                if screen:
                    g = screen.geometry()
                    if 0 <= x <= g.width() - self.width() and 0 <= y <= g.height() - self.height():
                        self._saved_pos = QPoint(x, y)
                        return
                self._saved_pos = None
            else:
                self._saved_pos = None
        except Exception:
            self._saved_pos = None

    def _save_position(self):
        try:
            pos = self.frameGeometry().topLeft()
            with open(self._POS_FILE, 'w') as f:
                json.dump({'x': pos.x(), 'y': pos.y()}, f)
        except Exception as e:
            log.error(f'[CountdownOverlay] 保存位置失败: {e}')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPos() - self.frameGeometry().topLeft()
            self.setCursor(Qt.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._drag_offset is not None:
            self.move(event.globalPos() - self._drag_offset)

    def mouseReleaseEvent(self, event):
        self._drag_offset = None
        self.setCursor(Qt.OpenHandCursor)
        self._save_position()

    def show_countdown(self, remaining_seconds, title, hint, total_seconds=300):
        self._total_seconds = total_seconds
        m = int(remaining_seconds // 60)
        s = int(remaining_seconds % 60)
        self.title_label.setText(title)
        self.timer_label.setText(f'{m:02d}:{s:02d}')
        self.hint_label.setText(hint)

        pct = int((remaining_seconds / min(total_seconds, remaining_seconds + 1)) * 100)
        self.progress_bar.setValue(max(pct, 0))

        if remaining_seconds <= 60:
            phase = math.sin(time.time() * 3)
            font_size = int(36 + phase * 3)
            color = '#FF8A70' if phase > 0 else '#FF6B50'
            self.timer_label.setStyleSheet(
                f'color: {color}; font-size: {font_size}px; font-weight: bold; font-family: Consolas; background: transparent; border: none;'
            )
            self.title_label.setStyleSheet('color: #FF6B50; font-size: 12px; font-weight: bold; background: transparent; border: none;')
        else:
            self.timer_label.setStyleSheet('color: #FFFFFF; font-size: 36px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
            self.title_label.setStyleSheet('color: #FFD93D; font-size: 12px; font-weight: bold; background: transparent; border: none;')

        if not self._chimed:
            self._chimed = True
            import threading
            threading.Thread(target=self._play_chime, daemon=True).start()

        if not self.isVisible():
            if self._saved_pos:
                self.move(self._saved_pos)
            else:
                screen = QApplication.primaryScreen()
                if screen:
                    g = screen.geometry()
                    self.move(g.width() - 220, 30)
            self.show()
        self.raise_()

    @staticmethod
    def _play_chime():
        try:
            winsound.Beep(880, 150)
            winsound.Beep(1100, 200)
        except Exception:
            pass

    def hide_overlay(self):
        self._chimed = False
        self.hide()


class VideoFetchThread(QThread):
    """获取 B 站视频列表的线程"""
    finished = pyqtSignal(list)

    def __init__(self, get_videos_fn, parent=None):
        super().__init__(parent)
        self._get_videos = get_videos_fn

    def run(self):
        try:
            videos = self._get_videos()
        except Exception as e:
            log.error(f'[VideoFetchThread] 获取视频异常：{e}')
            videos = []
        self.finished.emit(videos)


class RestReminderWidget(QWidget):
    def __init__(self, silent_start=False):
        super().__init__()
        self.interval_minutes = 60
        self.start_time = None
        self.remaining_when_paused = None
        self.timer_state = 'idle'
        self._battery_tick = 0

        # 视频相关
        self.video_list = []
        self.played_today = set()

        # 电池相关
        self.last_charging_state = None
        self.battery_warning_shown = False
        self.battery_notification_active = False

        # 日期检测
        self.current_date = datetime.now().date()

        # 学习时长（本地计数，每次倒计时完成算 1 小时）
        self.study_hours_today = 0

        # 电脑使用时长监控（每 3 小时提醒一次 + 飞书同步）
        self.computer_usage_hours_today = 0
        self.last_computer_usage_check = datetime.now()
        self.computer_usage_reminder_given_at = None  # 记录上次提醒的周期数
        self.computer_3h_cycles_today = 0  # 今天已完成的 3 小时周期数
        self._computer_usage_save_tick = 0  # 每 60 tick 保存一次
        self._load_computer_usage()

        # 5分钟倒计时浮层状态
        self._study_countdown_active = False
        self._computer_countdown_active = False

        self.drag_position = None

        self.init_ui()
        self.init_tray()
        self.set_autostart(True)
        self.setup_timer()
        # 创建小浮球
        self.floating_ball = FloatingBall(self)
        # 创建5分钟倒计时浮层
        self.countdown_overlay = CountdownOverlay()
        # 启动时先显示主窗口看看效果
        self.show()
        # 移到屏幕右侧
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.geometry()
            self.move(screen_geom.width() - 400, screen_geom.height() // 2 - 200)

    def init_ui(self):
        self.setWindowTitle('休息提醒')
        self.widget_width = 340
        self.widget_height = 380
        self.setGeometry(100, 100, self.widget_width, self.widget_height)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
        self.app_icon = QIcon(ico_path)
        self.setWindowIcon(self.app_icon)

        self.setStyleSheet("""
            QWidget {
                background-color: #141413;
                border-radius: 16px;
                color: #faf9f5;
            }
            QLabel {
                color: #faf9f5;
                font-size: 15px;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #b0aea5;
                border: none;
                font-size: 22px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton#closeBtn:hover {
                color: #faf9f5;
                background-color: rgba(255, 255, 255, 15);
            }
            QProgressBar {
                border: 2px solid #3a3a38;
                border-radius: 8px;
                text-align: center;
                background-color: #2a2a28;
                font-size: 13px;
                font-weight: 500;
            }
            QProgressBar::chunk {
                background-color: #d97757;
                border-radius: 6px;
            }
            #battery_bar::chunk {
                background-color: #788c57;
            }
            #battery_bar_low::chunk {
                background-color: #d95757;
            }
            #countdown_bar::chunk {
                background-color: #6a9bcc;
            }
            #computer_usage_bar::chunk {
                background-color: #9b6acc;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 12, 16, 16)
        main_layout.setSpacing(6)

        # 顶部：标题 + 最小化按钮
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel('⏰ 休息提醒')
        self.title_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 14, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.title_label.setStyleSheet('color: #faf9f5;')
        top_layout.addWidget(self.title_label)

        top_layout.addStretch()

        self.close_btn = QPushButton('×')
        self.close_btn.setObjectName('closeBtn')
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip('隐藏窗口')
        self.close_btn.clicked.connect(self.hide)
        top_layout.addWidget(self.close_btn)

        main_layout.addLayout(top_layout)

        # 时间显示
        self.time_label = QLabel('距离下次休息：60:00')
        self.time_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 16, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet('color: #d97757; padding: 5px 0;')
        main_layout.addWidget(self.time_label)

        # 按钮：开始/暂停
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton('▶ 开始')
        self.start_btn.setFont(QFont('Poppins, Microsoft YaHei, Arial', 11, QFont.Bold))
        self.start_btn.setFixedHeight(36)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #788c57;
                color: #faf9f5;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #8a9d66;
            }
        """)
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton('⏸ 暂停')
        self.pause_btn.setFont(QFont('Poppins, Microsoft YaHei, Arial', 11, QFont.Bold))
        self.pause_btn.setFixedHeight(36)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: #d97757;
                color: #faf9f5;
                border: none;
                border-radius: 8px;
                padding: 0 20px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #e68a66;
            }
            QPushButton:disabled {
                background-color: #3a3a38;
                color: #b0aea5;
            }
        """)
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        btn_layout.addWidget(self.pause_btn)

        main_layout.addLayout(btn_layout)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('%p%')
        main_layout.addWidget(self.progress_bar)

        # 22:00 倒计时
        self.countdown_label = QLabel('⏳ 距离 22:00:')
        self.countdown_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 12))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet('color: #6a9bcc; font-weight: 600; padding-top: 8px;')
        main_layout.addWidget(self.countdown_label)

        self.countdown_bar = QProgressBar()
        self.countdown_bar.setObjectName('countdown_bar')
        self.countdown_bar.setMaximum(100)
        self.countdown_bar.setValue(100)
        self.countdown_bar.setTextVisible(True)
        self.countdown_bar.setFormat('22:00')
        self.countdown_bar.setMaximumHeight(24)
        main_layout.addWidget(self.countdown_bar)

        # 学习时长进度条（14 小时=100%）
        self.study_progress_label = QLabel('📚 学习时长：0 小时')
        self.study_progress_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 12))
        self.study_progress_label.setAlignment(Qt.AlignCenter)
        self.study_progress_label.setStyleSheet('color: #d97757; font-weight: 600; padding-top: 8px;')
        main_layout.addWidget(self.study_progress_label)

        self.study_progress_bar = QProgressBar()
        self.study_progress_bar.setObjectName('study_bar')
        self.study_progress_bar.setMaximum(14)
        self.study_progress_bar.setValue(0)
        self.study_progress_bar.setTextVisible(True)
        self.study_progress_bar.setFormat('%v / 14 小时')
        self.study_progress_bar.setMaximumHeight(24)
        self.study_progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #3a3a38; border-radius: 8px; text-align: center; background-color: #2a2a28; font-size: 13px; font-weight: 500; }
            QProgressBar::chunk { background-color: #d97757; border-radius: 6px; }
        """)
        main_layout.addWidget(self.study_progress_bar)

        # 电脑使用时长
        self.computer_usage_label = QLabel('💻 今天电脑总使用：0H00min')
        self.computer_usage_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 12))
        self.computer_usage_label.setAlignment(Qt.AlignCenter)
        self.computer_usage_label.setStyleSheet('color: #9b6acc; font-weight: 600; padding-top: 8px;')
        main_layout.addWidget(self.computer_usage_label)

        self.computer_usage_bar = QProgressBar()
        self.computer_usage_bar.setObjectName('computer_usage_bar')
        self.computer_usage_bar.setMaximum(100)  # 100% = 3 小时（倒计时：100%→0%）
        self.computer_usage_bar.setValue(100)
        self.computer_usage_bar.setTextVisible(True)
        self.computer_usage_bar.setFormat('3H00min')
        self.computer_usage_bar.setMaximumHeight(24)
        main_layout.addWidget(self.computer_usage_bar)

        # 电池状态
        self.battery_label = QLabel('🔋 检测中...')
        self.battery_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 12))
        self.battery_label.setAlignment(Qt.AlignCenter)
        self.battery_label.setStyleSheet('color: #788c57; font-weight: 600; padding-top: 8px;')
        main_layout.addWidget(self.battery_label)

        self.battery_bar = QProgressBar()
        self.battery_bar.setObjectName('battery_bar')
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat('%p%')
        self.battery_bar.setMaximumHeight(24)
        main_layout.addWidget(self.battery_bar)

        self.setLayout(main_layout)

    def position_to_right(self):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.geometry()
            screen_width = screen_geom.width()
            screen_height = screen_geom.height()
        else:
            screen_width = 1920
            screen_height = 1080

        if '--center' in sys.argv:
            x = (screen_width - self.widget_width) // 2
            y = (screen_height - self.widget_height) // 2
            log.info(f"窗口居中显示：({x}, {y})")
        else:
            margin = 10
            x = screen_width - self.widget_width - margin
            y = (screen_height - self.widget_height) // 2
            log.info(f"窗口右侧显示：({x}, {y})")

        log.info(f"屏幕分辨率：{screen_width} x {screen_height}")
        self.move(x, y)

    def _get_autostart_cmd(self):
        script = os.path.abspath(sys.argv[0] if sys.argv[0].endswith('.py') else __file__)
        pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        return f'"{pythonw}" "{script}" --startup'

    def is_autostart_enabled(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, 'RestReminder')
            winreg.CloseKey(key)
            return bool(val)
        except (FileNotFoundError, OSError):
            return False

    def set_autostart(self, enabled):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Run', 0, winreg.KEY_SET_VALUE)
            if enabled:
                winreg.SetValueEx(key, 'RestReminder', 0, winreg.REG_SZ, self._get_autostart_cmd())
            else:
                try:
                    winreg.DeleteValue(key, 'RestReminder')
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
            return True
        except Exception as e:
            log.error(f'设置自启动失败：{e}')
            return False

    def toggle_autostart(self):
        new_state = not self.is_autostart_enabled()
        if self.set_autostart(new_state):
            self.autostart_action.setChecked(new_state)
            tip = '已开启' if new_state else '已关闭'
            self.tray_icon.showMessage('休息提醒', f'开机自启动{tip}', QSystemTrayIcon.Information, 2000)

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('休息提醒 - 双击显示/隐藏')
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        tray_menu = QMenu()

        toggle_action = QAction('显示/隐藏', self)
        toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(toggle_action)

        tray_menu.addSeparator()

        self.autostart_action = QAction('开机自启动', self)
        self.autostart_action.setCheckable(True)
        self.autostart_action.setChecked(self.is_autostart_enabled())
        self.autostart_action.triggered.connect(self.toggle_autostart)
        tray_menu.addAction(self.autostart_action)

        tray_menu.addSeparator()

        reset_position_action = QAction('重置位置到右侧', self)
        reset_position_action.triggered.connect(self.position_to_right)
        tray_menu.addAction(reset_position_action)

        tray_menu.addSeparator()

        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.show()

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()

    def toggle_visibility(self):
        """切换窗口可见性（不停止后台计时器——电池监控、电脑使用追踪等需持续运行）"""
        try:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
                self.raise_()
        except Exception as e:
            log.error(f'[toggle_visibility 异常] {type(e).__name__}: {e}')

    def hide_to_edge(self):
        """隐藏窗口到桌面右侧边缘（不停止后台计时器——只是视觉隐藏）"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                edge_width = 5
                x = screen_geometry.width() - edge_width
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
                log.info(f"已隐藏到右侧边缘，位置：({x}, {y})")
        except Exception as e:
            log.error(f'[hide_to_edge 异常] {type(e).__name__}: {e}')

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)

    _BTN_CONFIG = {
        'idle':    {'start_en': True,  'start_txt': '▶ 开始', 'pause_en': False, 'pause_txt': '⏸ 暂停'},
        'running': {'start_en': False, 'start_txt': '▶ 开始', 'pause_en': True,  'pause_txt': '⏸ 暂停'},
        'paused':  {'start_en': True,  'start_txt': '▶ 继续', 'pause_en': False, 'pause_txt': '⏸ 已暂停'},
    }

    def _sync_buttons(self):
        try:
            c = self._BTN_CONFIG[self.timer_state]
            self.start_btn.setEnabled(c['start_en'])
            self.start_btn.setText(c['start_txt'])
            self.pause_btn.setEnabled(c['pause_en'])
            self.pause_btn.setText(c['pause_txt'])
        except Exception as e:
            log.error(f'[_sync_buttons 异常] {type(e).__name__}: {e}')

    def on_start_clicked(self):
        try:
            if self.timer_state not in ('idle', 'paused'):
                return
            if self.timer_state == 'idle':
                self.start_time = datetime.now()
            else:
                self.start_time = datetime.now() - timedelta(seconds=(self.interval_minutes * 60 - self.remaining_when_paused))
            self.remaining_when_paused = None
            self.timer_state = 'running'
            self._sync_buttons()
        except Exception as e:
            log.error(f'[on_start_clicked 异常] {type(e).__name__}: {e}')

    def on_pause_clicked(self):
        try:
            if self.timer_state != 'running':
                return
            remaining = self.interval_minutes * 60 - (datetime.now() - self.start_time).total_seconds()
            self.remaining_when_paused = max(remaining, 0)
            self.timer_state = 'paused'
            self._sync_buttons()
        except Exception as e:
            log.error(f'[on_pause_clicked 异常] {type(e).__name__}: {e}')

    def _reset_timer_to_idle(self):
        try:
            self.timer_state = 'idle'
            self.start_time = None
            self.remaining_when_paused = None
            self._study_countdown_active = False
            # 学习倒计时结束，但电脑使用倒计时可能还在运行
            if not self._computer_countdown_active:
                self.countdown_overlay.hide_overlay()
            self._sync_buttons()
        except Exception as e:
            log.error(f'[_reset_timer_to_idle 异常] {type(e).__name__}: {e}')

    def _handle_idle(self):
        """处理空闲状态 - 显示默认时间"""
        self.time_label.setText(f'距离下次休息：{self.interval_minutes:02d}:00')
        self.progress_bar.setValue(0)

    def _handle_running(self, now):
        """处理运行状态 - 倒计时"""
        elapsed = (now - self.start_time).total_seconds()
        total_seconds = self.interval_minutes * 60
        remaining = max(total_seconds - elapsed, 0)

        # 更新显示
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        self.time_label.setText(f'距离下次休息：{mins:02d}:{secs:02d}')

        # 更新进度条
        progress = int((elapsed / total_seconds) * 100)
        self.progress_bar.setValue(min(progress, 100))

        # 最后5分钟倒计时浮层
        if remaining <= 300 and remaining > 0:
            self._study_countdown_active = True
            self.countdown_overlay.show_countdown(
                remaining,
                '📚 学习即将结束',
                '还剩不到5分钟，准备休息一下~',
                total_seconds=300
            )
        # 倒计时结束（包含浮层清理）
        if remaining <= 0:
            self._study_countdown_active = False
            # 不直接隐藏浮层：电脑使用倒计时可能还在运行
            if not self._computer_countdown_active:
                self.countdown_overlay.hide_overlay()
            self.open_random_video()
            self.study_hours_today += 1
            self.update_study_display()
            FeishuSync.increment_study_hour(self.study_hours_today)
            self._reset_timer_to_idle()

    def _handle_paused(self, now):
        """处理暂停状态 - 显示暂停时间"""
        mins = int(self.remaining_when_paused // 60)
        secs = int(self.remaining_when_paused % 60)
        self.time_label.setText(f'⏸ 已暂停：{mins:02d}:{secs:02d}')
        # 暂停时隐藏倒计时浮层，避免冻结显示
        if self._study_countdown_active:
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()

    def _update_countdown(self, now):
        """更新22:00倒计时"""
        target_time = now.replace(hour=22, minute=0, second=0, microsecond=0)
        if now >= target_time:
            # 如果已经过了22:00，显示明天22:00
            target_time = target_time + timedelta(days=1)

        diff = target_time - now
        total_seconds = diff.total_seconds()
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)

        self.countdown_label.setText(f'⏳ 距离 22:00 还有：{hours}小时{minutes}分钟')

        # 进度条从0点(100%)到22:00(0%)倒计时模式
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.hour >= 22:
            midnight = midnight + timedelta(days=1)
        seconds_since_midnight = (now - midnight).total_seconds()
        progress = 100 - int((seconds_since_midnight / (22 * 3600)) * 100)
        self.countdown_bar.setValue(max(progress, 0))

    def update_display(self):
        try:
            now = datetime.now()

            # --- 日期变化重置 ---
            if now.date() != self.current_date:
                # 重置数据
                self.played_today = set()
                self.study_hours_today = 0
                self.computer_usage_hours_today = 0
                self.computer_3h_cycles_today = 0
                self.computer_usage_reminder_given_at = None
                self._study_countdown_active = False
                self._computer_countdown_active = False
                self.countdown_overlay.hide_overlay()
                self.current_date = now.date()
                FeishuSync.reset()
                self._save_computer_usage()
                self.update_study_display()
                self.update_computer_usage_display()
                log.info(f'新的一天，数据已重置: {self.current_date}')

            # --- 状态机路由 ---
            if self.timer_state == 'idle':
                self._handle_idle()
            elif self.timer_state == 'running':
                self._handle_running(now)
            elif self.timer_state == 'paused':
                self._handle_paused(now)

            # --- 22:00 倒计时（统一更新，避免重复请求） ---
            self._update_countdown(now)

            # --- 每 15 秒电池检测 ---
            self._battery_tick += 1
            if self._battery_tick >= 15:
                self._battery_tick = 0
                self.update_battery_status()

            # --- 电脑使用时长累加与提醒 ---
            self.update_computer_usage(now)

        except Exception as e:
            log.error(f'[update_display 异常] {type(e).__name__}: {e}')
            traceback.print_exc()

    def update_study_display(self):
        """更新学习时长显示"""
        h = self.study_hours_today
        self.study_progress_label.setText(f'📚 学习时长：{h}小时')
        self.study_progress_bar.setValue(h)

    def _get_usage_cache_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.computer_usage.json')

    def _load_computer_usage(self):
        """从本地文件恢复今天的电脑使用计数（跨重启持久化）"""
        path = self._get_usage_cache_path()
        if not os.path.exists(path):
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('date') == self.current_date.isoformat():
                self.computer_usage_hours_today = data.get('hours', 0)
                self.computer_3h_cycles_today = data.get('cycles', 0)
                self.computer_usage_reminder_given_at = data.get('last_cycle', None)
                log.info(f'[ComputerUsage] 恢复今日计数: {self.computer_usage_hours_today:.2f}h, {self.computer_3h_cycles_today} 个周期')
        except Exception as e:
            log.error(f'[ComputerUsage] 加载缓存失败: {e}')

    def _save_computer_usage(self):
        """保存当前电脑使用计数到本地文件"""
        try:
            with open(self._get_usage_cache_path(), 'w', encoding='utf-8') as f:
                json.dump({
                    'date': self.current_date.isoformat(),
                    'hours': self.computer_usage_hours_today,
                    'cycles': self.computer_3h_cycles_today,
                    'last_cycle': self.computer_usage_reminder_given_at
                }, f, ensure_ascii=False)
        except Exception as e:
            log.error(f'[ComputerUsage] 保存缓存失败: {e}')

    def update_computer_usage(self, now):
        """更新电脑使用时长（倒计时模式：3 小时→0）"""
        # 每秒增加使用时长
        self.computer_usage_hours_today += 1 / 3600  # 每秒增加 1/3600 小时

        # 计算当前 3 小时周期内的已用时长（取模循环）
        cycle_usage = self.computer_usage_hours_today % 3

        # 更新标签：显示今天总使用时长（XXHXXmin 格式）
        total_h = int(self.computer_usage_hours_today)
        total_m = int((self.computer_usage_hours_today - total_h) * 60)
        self.computer_usage_label.setText(f'💻 今天电脑总使用：{total_h}H{total_m:02d}min')

        # 进度条倒计时：100%→0%（3 小时内）
        usage_pct = int((cycle_usage / 3) * 100)
        countdown_pct = 100 - usage_pct
        remaining_min = 3 - cycle_usage
        remaining_h = int(remaining_min)
        remaining_m = int((remaining_min - remaining_h) * 60)
        self.computer_usage_bar.setFormat(f'{remaining_h}H{remaining_m:02d}min')
        self.computer_usage_bar.setValue(countdown_pct)

        # 最后5分钟倒计时浮层
        remaining_seconds = remaining_min * 3600
        if remaining_seconds <= 300 and remaining_seconds > 0 and not self._study_countdown_active:
            self._computer_countdown_active = True
            self.countdown_overlay.show_countdown(
                remaining_seconds,
                '💻 电脑使用即将到期',
                '还剩不到5分钟，准备休息眼睛~',
                total_seconds=300
            )
        elif self._computer_countdown_active and (remaining_seconds > 300 or remaining_seconds <= 0):
            self._computer_countdown_active = False
            if not self._study_countdown_active:
                self.countdown_overlay.hide_overlay()

        # 每 3 小时触发一次（跨重启持久化计数）
        current_cycle = int(self.computer_usage_hours_today / 3)
        if current_cycle > self.computer_3h_cycles_today:
            self.computer_3h_cycles_today = current_cycle
            self.computer_usage_reminder_given_at = current_cycle
            self._computer_countdown_active = False
            self.countdown_overlay.hide_overlay()
            self.show_computer_usage_reminder(cycle=current_cycle)
            FeishuSync.increment_computer_hour(self.computer_usage_hours_today)
            self._save_computer_usage()
            log.info(f'[ComputerUsage] 触发第 {current_cycle} 个 3 小时周期，飞书同步={current_cycle}')
        else:
            # 每 60 秒保存一次计数（防止重启丢失），用 tick 计数器避免浮点精度问题
            self._computer_usage_save_tick += 1
            if self._computer_usage_save_tick >= 60:
                self._computer_usage_save_tick = 0
                self._save_computer_usage()

    def show_computer_usage_reminder(self, cycle=1):
        """电脑使用 3 小时后提醒，打开护眼视频"""
        total_h = int(self.computer_usage_hours_today)
        video_url = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click'
        open_url(video_url)
        self.tray_icon.showMessage(
            '💻 电脑使用时间过长',
            f'今天累计 {total_h} 小时（第 {cycle} 个周期），看看护眼视频休息一下眼睛吧~',
            QSystemTrayIcon.Information,
            5000
        )

    def update_computer_usage_display(self):
        """更新电脑使用时长显示（XXHXXmin 格式）"""
        total_h = int(self.computer_usage_hours_today)
        total_m = int((self.computer_usage_hours_today - total_h) * 60)
        self.computer_usage_label.setText(f'💻 今天电脑总使用：{total_h}H{total_m:02d}min')

        # 进度条倒计时
        cycle_usage = self.computer_usage_hours_today % 3
        usage_pct = int((cycle_usage / 3) * 100)
        countdown_pct = 100 - usage_pct
        remaining_min = 3 - cycle_usage
        remaining_h = int(remaining_min)
        remaining_m = int((remaining_min - remaining_h) * 60)
        self.computer_usage_bar.setFormat(f'{remaining_h}H{remaining_m:02d}min')
        self.computer_usage_bar.setValue(countdown_pct)

    def update_battery_status(self):
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                self.battery_label.setText('🖥️ 台式机（无电池）')
                self.battery_bar.setValue(100)
                self.battery_bar.setObjectName('battery_bar')
                self.battery_bar.setStyleSheet('')
                return

            percent = battery.percent
            plugged = battery.power_plugged

            self.battery_bar.setValue(int(percent))

            if percent <= 20:
                self.battery_bar.setObjectName('battery_bar_low')
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #d95757; }")
            else:
                self.battery_bar.setObjectName('battery_bar')
                self.battery_bar.setStyleSheet("QProgressBar::chunk { background-color: #788c57; }")

            if plugged:
                if percent >= 100:
                    icon, status = '🔌', '已充满'
                else:
                    icon, status = '⚡', '充电中'
                self.battery_label.setText(f'{icon} {status}')

                if self.battery_notification_active:
                    self.tray_icon.showMessage('', '', QSystemTrayIcon.NoIcon, 1)
                    self.battery_notification_active = False
                self.battery_warning_shown = False
            else:
                icon = '🔋'
                if percent <= 20:
                    status, icon = '电量低', '🪫'
                elif percent <= 50:
                    status = '电量中'
                else:
                    status = '使用电池'
                self.battery_label.setText(f'{icon} {status}')

                if self.last_charging_state is True and not plugged:
                    if not self.battery_warning_shown:
                        self.show_battery_warning(percent)
                        self.battery_warning_shown = True
                        self.battery_notification_active = True

            self.last_charging_state = plugged

        except Exception as e:
            self.battery_label.setText('❌ 电池状态获取失败')
            log.error(f'获取电池状态失败：{e}')

    def show_battery_warning(self, percent):
        self.tray_icon.showMessage(
            '⚠️ 电源已断开',
            f'检测到电脑未在充电！\n当前电量：{percent}%\n建议连接电源以保持最佳性能。',
            QSystemTrayIcon.Warning,
            5000
        )
        if self.isVisible():
            self.setWindowOpacity(0.5)
            QTimer.singleShot(200, lambda: self.setWindowOpacity(1.0))
            QTimer.singleShot(400, lambda: self.setWindowOpacity(0.5))
            QTimer.singleShot(600, lambda: self.setWindowOpacity(1.0))

    def get_bilibili_videos(self):
        """获取 B 站收藏夹视频列表（带重试）"""
        fid = '3648313921'
        mid = '529362421'

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
        ]

        for attempt in range(3):
            headers = {
                'User-Agent': user_agents[attempt % len(user_agents)],
                'Referer': 'https://www.bilibili.com',
                'Accept': 'application/json, text/plain, */*',
                'Origin': 'https://www.bilibili.com',
            }

            videos = []
            page = 1
            page_size = 20

            try:
                while True:
                    url = f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={fid}&pn={page}&ps={page_size}'
                    response = requests.get(url, headers=headers, timeout=10)
                    if response.status_code != 200:
                        break

                    data = response.json()
                    code = data.get('code')
                    if code != 0:
                        log.error(f'B 站 API 返回错误 code={code}, msg={data.get("message")} (尝试 {attempt+1}/3)')
                        break

                    medias = data.get('data', {}).get('medias') or []
                    if not medias:
                        break

                    for media in medias:
                        bvid = media.get('bvid')
                        if bvid and re.match(r'^BV[a-zA-Z0-9]{10}$', bvid):
                            videos.append(f'https://www.bilibili.com/video/{bvid}')

                    if len(medias) < page_size:
                        break
                    page += 1

                if videos:
                    log.info(f'获取到 {len(videos)} 个收藏视频（{page} 页，第{attempt+1}次尝试）')
                    return videos

            except Exception as e:
                log.error(f'获取视频列表异常 (尝试 {attempt+1}/3): {e}')

            if attempt < 2:
                time.sleep(2)

        # 兜底方案
        log.info('API 3 次全部失败，尝试从收藏夹页面提取视频链接...')
        try:
            page_url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create'
            resp = requests.get(page_url, headers={'User-Agent': user_agents[0], 'Referer': 'https://www.bilibili.com'}, timeout=10)
            bvids = re.findall(r'BV[a-zA-Z0-9]{10}', resp.text)
            seen = set()
            unique = []
            for bv in bvids:
                if bv not in seen:
                    seen.add(bv)
                    unique.append(bv)
            if unique:
                log.info(f'从页面兜底提取到 {len(unique)} 个视频')
                return [f'https://www.bilibili.com/video/{bv}' for bv in unique]
        except Exception as e:
            log.error(f'页面兜底也失败了：{e}')

        return []

    def open_random_video(self):
        """打开随机视频"""
        thread = VideoFetchThread(self.get_bilibili_videos)

        def on_videos_fetched(videos):
            try:
                self.video_list = videos
                if videos:
                    remaining = [v for v in videos if v not in self.played_today]
                    if not remaining:
                        log.info('当天视频已全部播放过，重置记录')
                        self.played_today = set()
                        remaining = videos

                    video_url = random.choice(remaining)
                    self.played_today.add(video_url)
                    log.info(f'打开视频：{video_url} (今日已播 {len(self.played_today)}/{len(self.video_list)})')
                    open_url(video_url)
                    self.tray_icon.showMessage(
                        '休息时间到！',
                        f'已为您打开休息视频（今日第{len(self.played_today)}个），记得放松一下哦~',
                        QSystemTrayIcon.Information,
                        3000
                    )
                else:
                    fallback_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create'
                    open_url(fallback_url)
                    self.tray_icon.showMessage('休息时间到！', '已为您打开收藏夹页面~', QSystemTrayIcon.Information, 3000)
            except Exception as e:
                log.error(f'[open_random_video 回调异常] {type(e).__name__}: {e}')
                traceback.print_exc()

        if hasattr(self, '_video_thread') and self._video_thread.isRunning():
            self._video_thread.wait(3000)

        self._video_thread = VideoFetchThread(self.get_bilibili_videos)
        self._video_thread.finished.connect(on_videos_fetched)
        self._video_thread.start()

    def mousePressEvent(self, event):
        try:
            if event.button() == Qt.LeftButton:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
                event.accept()
        except Exception as e:
            log.error(f'[mousePressEvent 异常] {type(e).__name__}: {e}')

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
        except Exception as e:
            log.error(f'[mouseMoveEvent 异常] {type(e).__name__}: {e}')

    def closeEvent(self, event):
        try:
            event.ignore()
            self.hide_to_edge()
        except Exception as e:
            log.error(f'[closeEvent 异常] {type(e).__name__}: {e}')

    def quit_app(self):
        try:
            self._save_computer_usage()
            self.timer.stop()
            self.tray_icon.hide()
            QApplication.quit()
        except Exception as e:
            log.error(f'[quit_app 异常] {type(e).__name__}: {e}')


def main():
    single = SingleInstanceChecker()

    if single.is_already_running():
        log.warning('休息提醒程序已经在运行中！')
        if '--silent' not in sys.argv:
            a = QApplication(sys.argv)
            QMessageBox.warning(None, '已在运行', '程序已在运行中！\n请检查系统托盘图标。')
        sys.exit(0)


    def excepthook(exc_type, exc_value, exc_tb):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        os._exit(1)
    sys.excepthook = excepthook

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    silent = '--silent' in sys.argv
    widget = RestReminderWidget(silent_start=silent)
    if silent:
        widget.hide()
    else:
        widget.show()

    # 全局异常处理器
    def widget_excepthook(exc_type, exc_value, exc_tb):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        os._exit(1)
    sys.excepthook = widget_excepthook

    try:
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
        hicon = ctypes.windll.user32.LoadImageW(0, ico_path, 1, 0, 0, 0x00000010)
        if hicon:
            hwnd = int(widget.winId())
            WM_SETICON = 0x0080
            ICON_SMALL = 0
            ICON_BIG = 1
            hicon_ptr = ctypes.c_void_p(hicon)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_SMALL, hicon_ptr)
            ctypes.windll.user32.SendMessageW(hwnd, WM_SETICON, ICON_BIG, hicon_ptr)
    except Exception as e:
        log.error(f'WM_SETICON error: {e}')

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
