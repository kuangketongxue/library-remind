"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
- 20-20-20 护眼提醒：每 20 分钟浮窗提示看远处 20 秒
- 监控电池充电状态
- 监控电脑使用时长（每 3 小时提醒）
- 学习时长本地计数（每次倒计时完成算 1 小时）
- 数据本地持久化（.daily_log.json）
"""
import sys
import time
import random
import hashlib
import uuid
import platform
import requests
import ctypes
import os
import tempfile
import re
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox, QShortcut, QInputDialog, QFrame, QTabWidget)
from PyQt5.QtCore import QTimer, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QBrush, QPen, QKeySequence
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import psutil
import atexit
import winreg
import traceback
import winsound
import logging
from logging.handlers import RotatingFileHandler
from storage import JSONStore

# 子目录模块需显式加入 sys.path
_PRO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest-reminder-pro')
if _PRO_DIR not in sys.path:
    sys.path.insert(0, _PRO_DIR)

# 日志配置：写入文件（pythonw 模式下 print 全部丢失），自动轮转 3×1MB
VERSION = 'v4.0'
_LOG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest_reminder.log')
_handler = RotatingFileHandler(_LOG_FILE, maxBytes=1_000_000, backupCount=3, encoding='utf-8')
_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', '%Y-%m-%d %H:%M:%S'))
log = logging.getLogger('rest_reminder')
log.setLevel(logging.INFO)
log.addHandler(_handler)

# ── 存储层（统一 JSON IO） ──
goal_store      = JSONStore('.goal.json',          default={},          ensure_ascii=False)
quotes_store    = JSONStore('.wisdom_quotes.json',  default=[])
daily_store     = JSONStore('.daily_log.json',      default={},          ensure_ascii=False)
settings_store  = JSONStore('.settings.json',       default={'reminder_mode': 'video'}, ensure_ascii=False)
streak_store    = JSONStore('.streak.json',         default={'current_streak': 0, 'last_streak_date': '', 'best_streak': 0}, ensure_ascii=False)
history_store   = JSONStore('.stats_history.json',  default={})
app_state_store = JSONStore('.app_state.json')
review_store    = JSONStore('.review_log.json',     default={},          ensure_ascii=False, indent=2)
computer_store  = JSONStore('.computer_usage.json', default={}, ensure_ascii=False)


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


# ── 请辨金句库 ──
WISDOM_QUOTES = [
    ("活下来是最重要的能力", "守富思维"),
    ("耐心本身就是门槛", "门槛前竞争"),
    ("5000块token碾压5000块人力", "Token经济"),
    ("先溢出，再消费", "财富积累"),
    ("反馈密度：3小时没新产出就有问题", "做事密度"),
    ("努力的目的=扩展自由的边界", "亿万富翁的忠告"),
    ("你今天享受的，是过去帝王都无法享受的", "技术进步"),
    ("主线清晰的人废寝忘食", "目标感"),
    ("休息是为了守富——巴菲特秘密=一直没死", "守富"),
    ("疯狂干上几周，立刻知道要不要继续", "行动力"),
    ("每件事指向未来会更好", "做事密度"),
    ("你不需要跑得有多快，只需要比躺平党快", "门槛前竞争"),
    ("安逸让人变笨——大脑和肌肉一样需要刺激", "认知"),
    ("「相互」是童年策略，不是成人策略", "人际关系"),
    ("赚钱能力是养出来的——浸泡在搞钱里", "赚钱"),
]


def _get_device_id():
    """基于机器名+MAC地址生成稳定设备 ID（同一台机器始终相同）"""
    return hashlib.md5(f"{platform.node()}-{uuid.getnode()}".encode()).hexdigest()[:12]


STREAK_MILESTONE = {
    1:    ("耐心本身就是门槛", "大部分人在你今天就开始累积了"),
    3:    ("门槛前竞争", "3天——抢门槛的人已经甩开一批了"),
    7:    ("复利游戏", "7天——复利开始滚动"),
    14:   ("习惯成自然", "两周——你已经超过90%的人"),
    30:   ("月度王者", "30天——坚持的力量"),
    60:   ("二月不败", "60天——你已经是别人的榜样"),
    90:   ("季度冠军", "90天——质的飞跃"),
    365:  ("年度传奇", "365天——你改变了自己"),
}

STREAK_THRESHOLD_HOURS = 4  # 每日学习满此小时数才算打卡

_GOAL_OPTIONS = ['学习/高考', '编程/开发', '写作/创作', '阅读/输入', '放松/无目标']

# 活动检测结构体：模块级定义避免每15秒重新创建
class _LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]


def _get_idle_seconds():
    """通过 Win32 API 获取系统空闲时间（秒）"""
    try:
        lii = _LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(_LASTINPUTINFO)
        ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii))
        millis = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return millis // 1000
    except Exception:
        log.warning('[空闲检测] Win32 API 失败')
        return 0


def _pick_quote():
    """从金句库中选一条未在今天展示过的"""
    used = quotes_store.load()
    available = [q for q in WISDOM_QUOTES if q[0] not in used]
    if not available:
        used.clear()
        available = list(WISDOM_QUOTES)
    picked = random.choice(available)
    used.append(picked[0])
    quotes_store.save(used)
    return picked


def _get_streak_milestone(streak):
    """获取打卡里程碑对应的金句（dict插入顺序=键升序）"""
    for k in reversed(list(STREAK_MILESTONE)):
        if streak >= k:
            return STREAK_MILESTONE[k]
    return None


class FloatingBall(QWidget):
    """小浮球，点击显示主窗口，右键菜单"""
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

        # 外层光晕
        painter.setBrush(QBrush(QColor(212, 175, 55, 25)))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(-4, -4, 68, 68)

        # 内层圆（渐变）
        painter.setBrush(QBrush(QColor(20, 20, 24)))
        painter.setPen(QPen(QColor(212, 175, 55, 80), 1.5))
        painter.drawEllipse(2, 2, 56, 56)

        # 图标
        painter.setPen(QColor(212, 175, 55))
        painter.setFont(QFont('Arial', 22, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, '⏰')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            self.click_time = datetime.now()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.dragging:
            self.dragging = False
            # 如果拖动距离很小，认为是点击
            delta = (datetime.now() - self.click_time).total_seconds()
            if delta < 0.3:
                self.toggle_main_window()

    def toggle_main_window(self):
        """显示/隐藏主窗口"""
        if self.main_window.isVisible():
            self.main_window.hide()
        else:
            self.main_window.show()
            self.main_window.activateWindow()
            self.main_window.raise_()

    def show_context_menu(self, pos):
        """显示右键菜单"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: rgba(20, 20, 24, 0.95);
                border: 1px solid rgba(212, 175, 55, 0.2);
                border-radius: 10px;
                padding: 6px;
            }
            QMenu::item {
                color: #e8e6e1;
                padding: 8px 16px;
                border-radius: 6px;
                font-family: Georgia, serif;
                font-size: 12px;
            }
            QMenu::item:selected {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QMenu::separator {
                height: 1px;
                background: rgba(255, 255, 255, 0.06);
                margin: 4px 8px;
            }
        """)

        # 打开主界面
        action_open = menu.addAction("🖥️  打开主界面")
        action_open.triggered.connect(self.open_main_window)

        # 打开官方网站
        action_website = menu.addAction("🌐  打开官方网站")
        action_website.triggered.connect(self.open_website)

        menu.addSeparator()

        # 退出
        action_quit = menu.addAction("✕  退出")
        action_quit.triggered.connect(self.quit_app)

        menu.exec_(pos)

    def open_main_window(self):
        """打开主窗口"""
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()

    def open_website(self):
        """打开官方网站"""
        open_url("https://024f119c.rest-reminder-app.pages.dev/")

    def quit_app(self):
        """退出应用"""
        self.main_window.quit_app()



class LocalSync:
    """本地存储学习/电脑使用时长（替代飞书同步）"""

    _data = None
    _current_date = None

    @classmethod
    def _load(cls):
        today = datetime.now().date().isoformat()
        if cls._data is not None and cls._current_date == today:
            return cls._data
        data = daily_store.load()
        if data.get('date') == today:
            cls._data = data
            cls._current_date = today
            return cls._data
        cls._data = {'date': today, 'study_hours': 0, 'computer_hours': 0, 'break_minutes_today': 0}
        cls._current_date = today
        return cls._data

    @classmethod
    def _save(cls):
        daily_store.save(cls._data)

    @classmethod
    def increment_study_hour(cls, total_hours):
        data = cls._load()
        data['study_hours'] = round(total_hours, 1)
        cls._save()
        log.info(f'[LocalSync] 学习时长: {total_hours}h')
        return True

    @classmethod
    def increment_computer_hour(cls, total_hours):
        data = cls._load()
        data['computer_hours'] = round(total_hours, 1)
        cls._save()
        log.info(f'[LocalSync] 电脑使用时长: {total_hours}h')
        return True

    @classmethod
    def load_study_hours(cls):
        """启动时恢复今日学习时长"""
        data = cls._load()
        return data.get('study_hours', 0)

    @classmethod
    def load_break_minutes(cls):
        """启动时恢复今日休息分钟数"""
        data = cls._load()
        return data.get('break_minutes_today', 0)

    @classmethod
    def save_break_minutes(cls, minutes):
        """保存今日休息分钟数"""
        data = cls._load()
        data['break_minutes_today'] = round(minutes, 1)
        cls._save()
        log.info(f'[LocalSync] 休息时长: {minutes:.1f}分钟')

    # --- 设置文件 (.settings.json) ---
    @classmethod
    def _get_settings_path(cls):
        return settings_store._path

    @classmethod
    def load_settings(cls):
        return settings_store.load()

    @classmethod
    def save_settings(cls, settings):
        settings_store.save(settings)
        log.info(f'[LocalSync] 设置已保存: {settings}')

    # --- 连续打卡 (.streak.json) ---
    @classmethod
    def _get_streak_path(cls):
        return streak_store._path

    @classmethod
    def load_streak(cls):
        return streak_store.load()

    @classmethod
    def save_streak(cls, streak_data):
        streak_store.save(streak_data)
        log.info(f'[LocalSync] 打卡记录: 连续{streak_data["current_streak"]}天, 最佳{streak_data["best_streak"]}天')

    # --- 历史统计 (.stats_history.json) ---
    @classmethod
    def _get_history_path(cls):
        return history_store._path

    @classmethod
    def save_daily_stats(cls):
        """保存今日数据到历史记录（每次调用都更新今日数据）"""
        data = cls._load()
        today = datetime.now().date().isoformat()
        history = history_store.load()
        history[today] = {
            'study': round(data.get('study_hours', 0), 1),
            'computer': round(data.get('computer_hours', 0), 1),
            'break_minutes': round(data.get('break_minutes_today', 0), 1)
        }
        # 只保留365天（支持年趋势）
        dates = sorted(history.keys())
        if len(dates) > 365:
            for old in dates[:len(dates) - 365]:
                del history[old]
        history_store.save(history)

    @classmethod
    def load_weekly_stats(cls):
        """加载最近7天的统计数据"""
        return history_store.load()

    @classmethod
    def reset(cls):
        cls._data = None
        cls._current_date = None

    # --- 应用状态 (.app_state.json) ---
    @classmethod
    def load_app_state(cls):
        """加载今日应用状态（计时器、休息、播放记录）"""
        today = datetime.now().date().isoformat()
        try:
            data = app_state_store.load()
        except FileNotFoundError:
            return None
        if data.get('date') == today:
            return data
        return None

    @classmethod
    def save_app_state(cls, state):
        """保存应用状态"""
        state['date'] = datetime.now().date().isoformat()
        app_state_store.save(state)


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
        except Exception as e:
            log.error(f'单实例检查失败：{e}')
            return self._fallback_check()

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
                    except Exception:
                        log.error("[LINE 557] 未捕获异常")
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
                except Exception:
                    log.error("[LINE 575] 未捕获异常")
                    pass
                self.lock_handle.close()
                self.lock_handle = None
            if self.lock_file and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except Exception:
            log.error("[LINE 582] 未捕获异常")
            pass


class DraggableOverlay(QWidget):
    """可拖动浮窗基类：共享拖动、位置记忆逻辑"""
    _POS_FILE = None  # 子类必须覆盖

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self._drag_offset = None
        self._saved_pos = None
        self.setCursor(Qt.OpenHandCursor)

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
            if self._POS_FILE:
                pos_store = JSONStore(os.path.basename(self._POS_FILE), default={'x': -1, 'y': -1})
                pos = pos_store.load()
                x, y = pos['x'], pos['y']
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
            log.warning("[位置] 加载位置失败")
            self._saved_pos = None

    def _save_position(self):
        try:
            pos = self.frameGeometry().topLeft()
            if self._POS_FILE:
                pos_store = JSONStore(os.path.basename(self._POS_FILE), default={'x': -1, 'y': -1})
                pos_store.save({'x': pos.x(), 'y': pos.y()})
        except Exception as e:
            log.error(f'[{type(self).__name__}] 保存位置失败: {e}')

    def _install_drag_on_children(self, *widgets):
        """为子控件安装事件过滤器以支持拖动"""
        for w in widgets:
            w.installEventFilter(self)


class CountdownOverlay(DraggableOverlay):
    """小型浮窗倒计时：拖动、位置记忆、进度条、呼吸动画、音效"""
    _POS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.overlay_pos.json')

    def __init__(self):
        super().__init__()
        self.setFixedSize(240, 130)

        self._total_seconds = 300
        self._remaining = 0
        self._chimed = False

        self.setStyleSheet("""
            background-color: rgba(20, 12, 8, 235);
            border-radius: 16px;
            border: 2px solid rgba(255, 200, 50, 0.55);
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(1)

        self.title_label = QLabel('')
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet('color: #FFC620; font-size: 14px; font-weight: bold; background: transparent; border: none;')

        self.timer_label = QLabel('')
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet('color: #FFFFFF; font-size: 44px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
        # 黑色发光阴影，白字在任何背景上都清晰
        _shadow = QGraphicsDropShadowEffect()
        _shadow.setBlurRadius(10)
        _shadow.setOffset(0, 0)
        _shadow.setColor(QColor(0, 0, 0, 200))
        self.timer_label.setGraphicsEffect(_shadow)

        self.hint_label = QLabel('')
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet('color: #cc9966; font-size: 12px; background: transparent; border: none;')

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background: rgba(255,255,255,0.08); border: none; border-radius: 3px; }
            QProgressBar::chunk { background: qlineargradient(x1:0, x2:1, stop:0 #6a9b6a, stop:0.5 #FFC620, stop:1 #FF6B50); border-radius: 3px; }
        """)

        layout.addWidget(self.title_label)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.progress_bar)

        self._install_drag_on_children(self.title_label, self.timer_label, self.hint_label, self.progress_bar)

        # 内部定时器：自己走秒，不再靠外部每秒 push
        self._internal_timer = QTimer(self)
        self._internal_timer.timeout.connect(self._internal_tick)

        self._load_position()
        self.hide()

    def show_countdown(self, remaining_seconds, title, hint, total_seconds=300):
        self._total_seconds = total_seconds
        self._remaining = remaining_seconds
        self.title_label.setText(title)
        self.hint_label.setText(hint)

        # 立即更新显示
        self._update_display()

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

        # 启动内部定时器（只有第一次启动，后续由内部 tick 处理）
        if not self._internal_timer.isActive():
            self._internal_timer.start(1000)

    def _update_display(self):
        """更新显示，不涉及窗口层级操作"""
        m = int(self._remaining // 60)
        s = int(self._remaining % 60)
        self.timer_label.setText(f'{m:02d}:{s:02d}')

        pct = self._remaining * 100 // self._total_seconds
        self.progress_bar.setValue(max(int(pct), 0))

        if self._remaining <= 60 and self._remaining > 0:
            # 最后60秒红色闪烁（每250ms交替，减少setStyleSheet频率）
            now_ms = int(time.time() * 1000)
            is_red_phase = (now_ms // 250) % 2 == 0
            if is_red_phase:
                self.timer_label.setStyleSheet('color: #FF2200; font-size: 48px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
            else:
                self.timer_label.setStyleSheet('color: #FF4A20; font-size: 44px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
            self.title_label.setStyleSheet('color: #FF4400; font-size: 15px; font-weight: bold; background: transparent; border: none;')
        else:
            self.timer_label.setStyleSheet('color: #FFFFFF; font-size: 44px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
            self.title_label.setStyleSheet('color: #FFC620; font-size: 14px; font-weight: bold; background: transparent; border: none;')

    def _internal_tick(self):
        """内部每秒 tick：递减剩余时间并更新显示"""
        self._remaining -= 1
        if self._remaining <= 0:
            self._internal_timer.stop()
            self.timer_label.setText('00:00')
            self.progress_bar.setValue(0)
            return  # 由外部负责隐藏
        self._update_display()

    @staticmethod
    def _play_notes(notes):
        """播放一组音阶提示音：notes=[(freq, duration, sleep_after), ...]"""
        try:
            for freq, dur, slp in notes:
                winsound.Beep(freq, dur)
                if slp:
                    time.sleep(slp)
        except Exception:
            log.error("[LINE 779] 未捕获异常")
            pass

    @staticmethod
    def _play_chime():
        """播放柔和的三音阶提示音（C-E-G 上行琶音）"""
        CountdownOverlay._play_notes([
            (523, 100, 0.08),   # C5
            (659, 100, 0.08),   # E5
            (784, 180, 0),      # G5
        ])

    @staticmethod
    def _play_rest_chime():
        """休息提醒提示音 — 轻柔两下，不打扰"""
        CountdownOverlay._play_notes([
            (660, 80, 0.05),
            (880, 120, 0),
        ])

    def hide_overlay(self):
        self._chimed = False
        if self._internal_timer.isActive():
            self._internal_timer.stop()
        self.hide()


class EyeRestOverlay(DraggableOverlay):
    """20-20-20 护眼提醒浮窗：轻量、自动消失、不打断学习流"""
    _POS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.eye_rest_pos.json')
    _COUNTDOWN_STYLE = 'color: #FFFFFF; font-size: 20px; font-weight: bold; font-family: Consolas; background: transparent; border: none;'
    _DONE_STYLE = 'color: #78B450; font-size: 20px; font-weight: bold; font-family: Consolas; background: transparent; border: none;'

    def __init__(self):
        super().__init__()
        self.setFixedSize(260, 90)

        self.setStyleSheet("""
            background-color: rgba(20, 30, 20, 220);
            border-radius: 14px;
            border: 1.5px solid rgba(120, 180, 80, 0.4);
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 10, 14, 8)
        layout.setSpacing(3)

        self.icon_label = QLabel('👁️ 看看远处')
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet('color: #78B450; font-size: 13px; font-weight: bold; background: transparent; border: none;')

        self.hint_label = QLabel('看 6 米以外的东西 20 秒')
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet('color: #b0d090; font-size: 11px; background: transparent; border: none;')

        self.countdown_label = QLabel('20')
        self.countdown_label.setAlignment(Qt.AlignCenter)
        self.countdown_label.setStyleSheet(self._COUNTDOWN_STYLE)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.hint_label)
        layout.addWidget(self.countdown_label)

        self._install_drag_on_children(self.icon_label, self.hint_label, self.countdown_label)

        self._auto_hide_timer = QTimer(self)
        self._auto_hide_timer.setSingleShot(True)
        self._auto_hide_timer.timeout.connect(self.hide_overlay)

        self._countdown_timer = QTimer(self)
        self._countdown_timer.timeout.connect(self._tick)
        self._remaining = 0

        self._load_position()
        self.hide()

    def show_reminder(self):
        """显示护眼提醒，15 秒后自动消失"""
        self._remaining = 20
        self.countdown_label.setText('20')
        self.countdown_label.setStyleSheet(self._COUNTDOWN_STYLE)

        if not self.isVisible():
            if self._saved_pos:
                self.move(self._saved_pos)
            else:
                screen = QApplication.primaryScreen()
                if screen:
                    g = screen.geometry()
                    self.move(g.width() - 280, 40)
            self.show()
        self.raise_()

        self._countdown_timer.start(1000)
        self._auto_hide_timer.start(15000)

    def _tick(self):
        self._remaining -= 1
        if self._remaining <= 0:
            self._countdown_timer.stop()
            self.countdown_label.setText('✓')
            self.countdown_label.setStyleSheet(self._DONE_STYLE)
            self.icon_label.setText('👁️ 好了~')
            self.hint_label.setText('眼睛舒服一点了吧')
        else:
            self.countdown_label.setText(str(self._remaining))

    def hide_overlay(self):
        self._countdown_timer.stop()
        self._auto_hide_timer.stop()
        if self.isVisible():
            self.icon_label.setText('👁️ 看看远处')
            self.hint_label.setText('看 6 米以外的东西 20 秒')
            self.countdown_label.setStyleSheet(self._COUNTDOWN_STYLE)
        self.hide()


class StatsWindow(QWidget):
    """学习统计窗口 - 显示最近7天的学习/电脑使用柱状图"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle('📊 学习统计')
        self.setFixedSize(420, 320)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setStyleSheet("""
            QWidget { background-color: #141413; color: #faf9f5; }
            QLabel { color: #faf9f5; }
            QPushButton#closeBtn {
                background-color: transparent; color: #b0aea5; border: none;
                font-size: 18px; font-weight: bold; padding: 0px;
            }
            QPushButton#closeBtn:hover { color: #faf9f5; background-color: rgba(255,255,255,15); }
        """)
        self._drag_pos = None

        # 关闭按钮
        close_btn = QPushButton('✕', self)
        close_btn.setObjectName('closeBtn')
        close_btn.setFixedSize(28, 28)
        close_btn.move(388, 4)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 标题
        painter.setPen(QColor('#faf9f5'))
        painter.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        painter.drawText(20, 25, '📊 最近7天学习统计')

        # 获取数据
        history = LocalSync.load_weekly_stats()
        today = datetime.now().date()
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            label = (today - timedelta(days=i)).strftime('%m/%d')
            data = history.get(d, {'study': 0, 'computer': 0})
            days.append({'label': label, 'study': data.get('study', 0), 'computer': data.get('computer', 0)})

        # 找最大值
        max_val = max(max(d['study'], d['computer']) for d in days) if days else 1
        max_val = max(max_val, 1)

        # 画柱状图
        chart_top = 50
        chart_bottom = 260
        chart_height = chart_bottom - chart_top
        bar_width = 20
        gap = (380 - 7 * bar_width * 2) / 8

        for i, d in enumerate(days):
            x = 30 + i * (bar_width * 2 + gap)

            # 学习柱子（绿色）
            h = int((d['study'] / max_val) * chart_height)
            painter.setBrush(QBrush(QColor('#788C57')))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(int(x), chart_bottom - h, bar_width, h, 3, 3)

            # 电脑使用柱子（橙色）
            h2 = int((d['computer'] / max_val) * chart_height)
            painter.setBrush(QBrush(QColor('#d97757')))
            painter.drawRoundedRect(int(x + bar_width + 2), chart_bottom - h2, bar_width, h2, 3, 3)

            # 日期标签
            painter.setPen(QColor('#b0aea5'))
            painter.setFont(QFont('Microsoft YaHei', 8))
            painter.drawText(int(x), chart_bottom + 15, d['label'])

            # 数值标签
            if d['study'] > 0:
                painter.setPen(QColor('#788C57'))
                painter.drawText(int(x), chart_bottom - h - 5, f"{d['study']:.1f}")
            if d['computer'] > 0:
                painter.setPen(QColor('#d97757'))
                painter.drawText(int(x + bar_width + 2), chart_bottom - h2 - 5, f"{d['computer']:.1f}")

        # 图例
        painter.setBrush(QBrush(QColor('#788C57')))
        painter.drawRect(30, 285, 12, 12)
        painter.setPen(QColor('#faf9f5'))
        painter.setFont(QFont('Microsoft YaHei', 9))
        painter.drawText(48, 296, '学习')

        painter.setBrush(QBrush(QColor('#d97757')))
        painter.drawRect(100, 285, 12, 12)
        painter.drawText(118, 296, '电脑使用')

        # 总计
        total_study = sum(d['study'] for d in days)
        painter.setPen(QColor('#6a9bcc'))
        painter.setFont(QFont('Microsoft YaHei', 9))
        painter.drawText(250, 296, f'本周学习：{total_study:.1f} 小时')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class TrendWindow(QWidget):
    """趋势分析窗口 — 5标签页：今日复盘时间线 | 周趋势 | 月趋势 | 季/年趋势 | 时段分析"""
    def __init__(self):
        super().__init__()
        log.info('[TrendWindow] 构造中...')
        self.setWindowTitle('📊 趋势分析')
        self.setFixedSize(520, 480)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setStyleSheet("""
            QWidget { background-color: #0c0c10; color: #e8e6e1; }
            QTabWidget::pane { background: #0c0c10; border: 1px solid #222; border-top: none; }
            QTabBar::tab {
                background: #14141a; color: #888; border: none; padding: 8px 14px;
                font-size: 11px; font-family: 'Georgia, "Noto Serif SC", serif';
                min-width: 70px;
            }
            QTabBar::tab:selected { color: #d4af37; background: #0c0c10; border-bottom: 2px solid #d4af37; }
            QTabBar::tab:hover { color: #e8e6e1; }
        """)
        self._drag_pos = None

        # 布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setFixedHeight(36)
        title_bar.setStyleSheet('background: #14141a;')
        t_layout = QHBoxLayout(title_bar)
        t_layout.setContentsMargins(14, 0, 8, 0)
        title_lbl = QLabel('📊 趋势分析')
        title_lbl.setStyleSheet('color: #d4af37; font-size: 12px; font-weight: bold; font-family: Georgia; background: transparent;')
        t_layout.addWidget(title_lbl)
        t_layout.addStretch()
        close_btn = QPushButton('✕')
        close_btn.setFixedSize(24, 24)
        close_btn.setStyleSheet('color: #555; background: transparent; border: none; font-size: 16px;')
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)
        t_layout.addWidget(close_btn)
        layout.addWidget(title_bar)

        # 选项卡
        self.tabs = QTabWidget()
        self.tabs.tabBar().setCursor(Qt.PointingHandCursor)
        layout.addWidget(self.tabs)

        # 5个标签页
        self._review_tab = QWidget()
        self._week_tab = QWidget()
        self._month_tab = QWidget()
        self._quarter_tab = QWidget()
        self._time_tab = QWidget()

        for tab, name in [
            (self._review_tab, '今日时间线'),
            (self._week_tab, '周趋势'),
            (self._month_tab, '月趋势'),
            (self._quarter_tab, '季/年趋势'),
            (self._time_tab, '时段分析'),
        ]:
            tab.setStyleSheet('background: #0c0c10;')
            self.tabs.addTab(tab, name)

        self.tabs.currentChanged.connect(self._refresh_active_tab)

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(50, self._refresh_active_tab)

    def _refresh_active_tab(self):
        try:
            idx = self.tabs.currentIndex()
            if idx == 0:
                self._draw_review_timeline()
            elif idx == 1:
                self._draw_weekly_trend()
            elif idx == 2:
                self._draw_monthly_trend()
            elif idx == 3:
                self._draw_quarterly_trend()
            elif idx == 4:
                self._draw_time_analysis()
        except Exception as e:
            import traceback
            log.error(f'[TrendWindow] 刷新标签页失败: {type(e).__name__}: {e}')
            traceback.print_exc()

    def _clear_tab(self, tab):
        """安全清除标签页内容"""
        old = tab.layout()
        if old:
            # 逐个取出所有子控件，移出并标记删除
            while old.count():
                item = old.takeAt(0)
                if item and item.widget():
                    item.widget().setParent(None)
                    item.widget().deleteLater()
        # 创建新布局
        l = QVBoxLayout(tab)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(6)
        return l

    # ── Tab 1: 今日复盘时间线 ──
    def _draw_review_timeline(self):
        reviews = review_store.load()
        today = datetime.now().date().isoformat()
        entries = reviews.get(today, [])
        layout = self._clear_tab(self._review_tab)

        if not entries:
            layout.addWidget(QLabel('📭 今天还没有复盘记录'))
            layout.addStretch()
            return

        # 顶部摘要
        scores = [e['score'] for e in entries]
        avg = sum(scores) / len(scores)
        peak = max(enumerate(scores), key=lambda x: x[1])
        low = min(enumerate(scores), key=lambda x: x[1])
        summary = QLabel(f'今日复盘 {len(entries)} 次 · 平均 {avg:.1f}⭐ · 最高 {entries[peak[0]]["time"]}({peak[1]}⭐) · 最低 {entries[low[0]]["time"]}({low[1]}⭐)')
        summary.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent; padding: 6px 0;')
        layout.addWidget(summary)

        # 时间线（每条记录一行）
        for e in entries:
            row = QHBoxLayout()
            row.setSpacing(8)

            # 时间
            t = QLabel(e['time'])
            t.setStyleSheet('color: #6a8cbb; font-size: 11px; font-family: Consolas; background: transparent; min-width: 44px;')
            t.setFixedWidth(44)
            row.addWidget(t)

            # 评分条
            bar_bg = QWidget()
            bar_bg.setFixedHeight(22)
            bar_bg.setStyleSheet('background: #1a1a20; border-radius: 4px;')
            bar_l = QHBoxLayout(bar_bg)
            bar_l.setContentsMargins(2, 2, 2, 2)

            fill = QWidget()
            pct = e['score'] / 5 * 100
            colors = {1: '#ff4444', 2: '#ff8844', 3: '#fcc419', 4: '#78B450', 5: '#51cf66'}
            fill.setFixedWidth(int(pct * 3))
            fill.setFixedHeight(18)
            fill.setStyleSheet(f'background: {colors.get(e["score"], "#555")}; border-radius: 3px;')
            bar_l.addWidget(fill)
            bar_l.addStretch()
            row.addWidget(bar_bg, 1)

            # 星级
            s = QLabel(f'{"⭐" * e["score"]}')
            s.setStyleSheet(f'color: {colors.get(e["score"], "#555")}; font-size: 11px; background: transparent; min-width: 70px;')
            s.setFixedWidth(70)
            row.addWidget(s)

            layout.addLayout(row)

        layout.addStretch()

    # ── Tab 2: 周趋势 ──
    def _draw_weekly_trend(self):
        stats = history_store.load()
        today = datetime.now().date()
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            label = (today - timedelta(days=i)).strftime('%m/%d')
            data = stats.get(d, {})
            days.append({
                'label': label, 'study': data.get('study', 0), 'computer': data.get('computer', 0)
            })

        layout = self._clear_tab(self._week_tab)
        self._draw_dual_bar(layout, days)

    # ── Tab 3: 月趋势 ──
    def _draw_monthly_trend(self):
        stats = history_store.load()
        today = datetime.now().date()
        # 最近30天按周聚合
        weeks = []
        for week_offset in range(4, -1, -1):
            week_start = today - timedelta(days=today.weekday() + 7 * week_offset)
            week_end = week_start + timedelta(days=6)
            if week_end > today:
                week_end = today
            study = computer = 0
            d = week_start
            while d <= week_end:
                k = d.isoformat()
                if k in stats:
                    study += stats[k].get('study', 0)
                    computer += stats[k].get('computer', 0)
                d += timedelta(days=1)
            weeks.append({
                'label': f'{week_start.month}/{week_start.day}',
                'study': round(study, 1), 'computer': round(computer, 1)
            })

        layout = self._clear_tab(self._month_tab)
        # 标题
        t = QLabel('📅 最近5周趋势（周聚合）')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)
        self._draw_dual_bar(layout, weeks)

    # ── Tab 4: 季/年趋势 ──
    def _draw_quarterly_trend(self):
        stats = history_store.load()
        today = datetime.now().date()
        # 按月聚合
        months = {}
        for d_str, data in stats.items():
            try:
                d = datetime.strptime(d_str, '%Y-%m-%d').date()
                key = d.strftime('%Y-%m')
                if key not in months:
                    months[key] = {'study': 0, 'computer': 0, 'count': 0}
                months[key]['study'] += data.get('study', 0)
                months[key]['computer'] += data.get('computer', 0)
                months[key]['count'] += 1
            except Exception:
                log.warning("[趋势] 日期解析跳过")
                continue

        if not months:
            layout = self._clear_tab(self._quarter_tab)
            layout.addWidget(QLabel('📭 数据不足，再积累几天就能看到趋势了'))
            layout.addStretch()
            return

        # 按时间排序
        sorted_months = sorted(months.keys())
        # 取最近6个月
        recent = sorted_months[-6:]
        month_data = []
        for m in recent:
            d = months[m]
            month_data.append({
                'label': m[5:],  # MM
                'study': round(d['study'], 1),
                'computer': round(d['computer'], 1)
            })

        layout = self._clear_tab(self._quarter_tab)
        t = QLabel('📈 近半年月度趋势')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)

        if len(month_data) >= 2:
            self._draw_dual_bar(layout, month_data)
        else:
            layout.addWidget(QLabel('📭 数据不足，再积累几天就能看到趋势了'))
            layout.addStretch()

        # 总览统计
        total_study = sum(d['study'] for d in month_data)
        total_computer = sum(d['computer'] for d in month_data)
        total_days = sum(d['count'] for d in months.values())
        avg_study = round(total_study / total_days, 1) if total_days else 0
        summary = QLabel(f'📊 统计周期内共 {total_days} 天 · 日均学习 {avg_study}h · 总学习 {total_study:.0f}h · 总电脑 {total_computer:.0f}h')
        summary.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent; padding: 6px 0;')
        layout.addWidget(summary)

    # ── Tab 5: 时段分析 ──
    def _draw_time_analysis(self):
        reviews = review_store.load()
        layout = self._clear_tab(self._time_tab)

        # ── 近7天日均评分对比（新增） ──
        today = datetime.now().date()
        daily_avgs = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            entries = reviews.get(d, [])
            if entries:
                scores = [e['score'] for e in entries]
                avg = round(sum(scores) / len(scores), 1)
                daily_avgs.append({
                    'label': (today - timedelta(days=i)).strftime('%m/%d'),
                    'avg': avg,
                    'count': len(scores)
                })
            else:
                daily_avgs.append({
                    'label': (today - timedelta(days=i)).strftime('%m/%d'),
                    'avg': 0,
                    'count': 0
                })

        if any(d['count'] > 0 for d in daily_avgs):
            t = QLabel('📅 近7天日均评分对比')
            t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
            layout.addWidget(t)

            for d in daily_avgs:
                row = QHBoxLayout()
                row.setSpacing(6)
                hl = QLabel(d['label'])
                hl.setStyleSheet('color: #6a8cbb; font-size: 11px; font-family: Consolas; background: transparent; min-width: 40px;')
                hl.setFixedWidth(40)
                row.addWidget(hl)

                bar_bg = QWidget()
                bar_bg.setFixedHeight(18)
                bar_bg.setStyleSheet('background: #1a1a20; border-radius: 4px;')
                bar_l = QHBoxLayout(bar_bg)
                bar_l.setContentsMargins(2, 2, 2, 2)
                fill = QWidget()
                if d['count'] > 0:
                    pct = d['avg'] / 5 * 100
                    fill.setFixedWidth(int(pct * 3))
                    fill.setFixedHeight(14)
                    fill_style = '#51cf66' if d['avg'] >= 4 else '#fcc419' if d['avg'] >= 3 else '#ff8844'
                else:
                    fill.setFixedWidth(0)
                    fill_style = 'transparent'
                fill.setStyleSheet(f'background: {fill_style}; border-radius: 3px;')
                bar_l.addWidget(fill)
                bar_l.addStretch()
                row.addWidget(bar_bg, 1)

                if d['count'] > 0:
                    sl = QLabel(f'{d["avg"]}⭐')
                    sl.setStyleSheet(f'color: #b0aea5; font-size: 11px; background: transparent; min-width: 36px;')
                    sl.setFixedWidth(36)
                    row.addWidget(sl)
                else:
                    sl = QLabel('—')
                    sl.setStyleSheet('color: #555; font-size: 11px; background: transparent; min-width: 36px;')
                    sl.setFixedWidth(36)
                    row.addWidget(sl)

                layout.addLayout(row)

            layout.addSpacing(12)

        # ── 原有的按小时聚合分析 ──
        # 按小时聚合所有评分
        hour_scores = {}  # hour -> [scores]
        for date_str, entries in reviews.items():
            for e in entries:
                try:
                    h = int(e['time'].split(':')[0])
                    if h not in hour_scores:
                        hour_scores[h] = []
                    hour_scores[h].append(e['score'])
                except Exception:
                    continue

        if not hour_scores:
            layout.addWidget(QLabel('📭 暂无复盘数据，每学习1小时复盘一次就能看到时段分析了'))
            layout.addStretch()
            return

        t = QLabel('⏰ 各时段专注度分析（聚合所有历史数据）')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)

        # 排序
        hours = sorted(hour_scores.keys())
        avg_scores = {h: round(sum(scores) / len(scores), 1) for h, scores in hour_scores.items()}
        counts = {h: len(scores) for h, scores in hour_scores.items()}

        # 最高/最低时段
        best_h = max(avg_scores, key=avg_scores.get)
        worst_h = min(avg_scores, key=avg_scores.get)
        info = QLabel(f'🏆 最佳时段: {best_h}:00-{best_h+1}:00 ({avg_scores[best_h]}⭐) · ⚠️ 待改进: {worst_h}:00-{worst_h+1}:00 ({avg_scores[worst_h]}⭐)')
        info.setStyleSheet('color: #b0aea5; font-size: 11px; background: transparent; padding-bottom: 4px;')
        layout.addWidget(info)

        for h in hours:
            row = QHBoxLayout()
            row.setSpacing(6)

            # 时段标签
            hl = QLabel(f'{h:02d}:00')
            hl.setStyleSheet('color: #6a8cbb; font-size: 11px; font-family: Consolas; background: transparent; min-width: 36px;')
            hl.setFixedWidth(36)
            row.addWidget(hl)

            # 评分条
            avg = avg_scores[h]
            bar_bg = QWidget()
            bar_bg.setFixedHeight(20)
            bar_bg.setStyleSheet('background: #1a1a20; border-radius: 4px;')
            bar_l = QHBoxLayout(bar_bg)
            bar_l.setContentsMargins(2, 2, 2, 2)

            fill = QWidget()
            pct = avg / 5 * 100
            fill.setFixedWidth(int(pct * 3))
            fill.setFixedHeight(16)
            fill_style = '#51cf66' if avg >= 4 else '#fcc419' if avg >= 3 else '#ff8844'
            fill.setStyleSheet(f'background: {fill_style}; border-radius: 3px;')
            bar_l.addWidget(fill)
            bar_l.addStretch()
            row.addWidget(bar_bg, 1)

            # 评分 + 次数
            sl = QLabel(f'{avg}⭐ ×{counts[h]}')
            sl.setStyleSheet(f'color: {fill_style}; font-size: 11px; background: transparent; min-width: 56px;')
            sl.setFixedWidth(56)
            row.addWidget(sl)

            layout.addLayout(row)

        layout.addStretch()

    # ── 双柱状图绘制（复用 ──
    def _draw_dual_bar(self, layout, data):
        """在 layout 中绘制学习(绿)+电脑(橙)双柱图"""
        chart = QWidget()
        chart.setFixedHeight(260)
        chart.setStyleSheet('background: transparent;')

        def paint_chart(painter, chart_widget):
            painter.setRenderHint(QPainter.Antialiasing)
            n = len(data)
            if n == 0:
                return
            max_val = max(max(d['study'], d['computer']) for d in data)
            max_val = max(max_val, 1)
            w = chart_widget.width()
            h = chart_widget.height()
            chart_top = 10
            chart_bottom = h - 40
            chart_height = chart_bottom - chart_top
            bar_w = min(20, int((w - 60) / (n * 2 + 1)))
            gap = int((w - 60 - n * bar_w * 2) / (n + 1))

            for i, d in enumerate(data):
                x = 30 + gap + i * (bar_w * 2 + gap)

                # 学习（绿）
                h_study = int((d['study'] / max_val) * chart_height)
                painter.setBrush(QBrush(QColor('#78B450')))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, chart_bottom - h_study, bar_w, h_study, 2, 2)

                # 电脑（橙）
                h_comp = int((d['computer'] / max_val) * chart_height)
                painter.setBrush(QBrush(QColor('#d97757')))
                painter.drawRoundedRect(x + bar_w + 2, chart_bottom - h_comp, bar_w, h_comp, 2, 2)

                # 日期
                painter.setPen(QColor('#888'))
                painter.setFont(QFont('Microsoft YaHei', 8))
                painter.drawText(x, chart_bottom + 16, d['label'])

                # 数值
                if d['study'] > 0:
                    painter.setPen(QColor('#78B450'))
                    painter.drawText(x, chart_bottom - h_study - 4, f"{d['study']:.1f}")
                if d['computer'] > 0:
                    painter.setPen(QColor('#d97757'))
                    painter.drawText(x + bar_w + 2, chart_bottom - h_comp - 4, f"{d['computer']:.1f}")

        chart.paintEvent = lambda e: paint_chart(QPainter(chart), chart)
        layout.addWidget(chart)

        # 图例
        legend = QLabel('🟢 学习 · 🟠 电脑使用')
        legend.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        layout.addWidget(legend)

        # 总计
        total_study = sum(d['study'] for d in data)
        total_comp = sum(d['computer'] for d in data)
        avg_study = round(total_study / len(data), 1)
        avg_comp = round(total_comp / len(data), 1)
        summary = QLabel(f'总计: 学习 {total_study:.1f}h · 电脑 {total_comp:.1f}h  |  日均: 学习 {avg_study}h · 电脑 {avg_comp}h')
        summary.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        layout.addWidget(summary)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def mouseReleaseEvent(self, event):
        self._drag_pos = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()


class RestReminderWidget(QWidget):
    def __init__(self, silent_start=False):
        super().__init__()
        self.start_time = None
        self.remaining_when_paused = None
        self.timer_state = 'idle'
        self._battery_tick = 0
        self._stats_tick = 0  # 每300tick(5分钟)保存历史统计
        self._state_save_tick = 0  # 每30tick(30秒)保存运行状态


        # 视频相关
        self.video_list = []
        self._video_cache_time = 0
        self._video_cache_ttl = 300  # 5分钟缓存
        self.played_today = set()

        # 22:00 每日汇报标记（每天只弹一次）
        self._daily_report_shown_today = False

        # 电池相关
        self.last_charging_state = None
        self.battery_warning_shown = False
        self.battery_notification_active = False

        # 日期检测
        self.current_date = datetime.now().date()

        # 学习时长（本地计数，每次倒计时完成算 1 小时）
        self.study_hours_today = LocalSync.load_study_hours()

        # 休息时长追踪
        self.break_start = None  # 倒计时结束时记录的时间戳
        self.break_minutes_today = LocalSync.load_break_minutes()

        # 连续打卡
        self.streak_data = LocalSync.load_streak()

        # 提醒方式设置
        self.app_settings = LocalSync.load_settings()
        self._bilibili_dns_error_logged = False  # DNS 错误只记一次，避免刷屏

        # 电脑使用时长（简单累计，无3小时提醒）
        self.computer_usage_ticks = 0  # 每秒+1，/3600=hours
        self._computer_save_tick = 0

        # 5分钟倒计时浮层状态
        self._study_countdown_active = False

        # 计时规则：固定60分钟学习 → 5分钟倒计时 → 5分钟休息 → 固定B站URL
        self._activity_interval = 60  # 固定60分钟
        self._round_count = 0  # 已完成的学习轮数（每轮=1小时学习+5分钟休息）
        self._rest_break_tick = 0

        # 目标锚点
        today = datetime.now().date().isoformat()
        d = goal_store.load()
        self.goal_text = d.get('goal', '') if d.get('date') == today else ''

        # 快速复盘
        self._pending_review = False

        # 20-20-20 护眼提醒
        self.eye_rest_interval = 20 * 60  # 20 分钟（秒）
        self.eye_rest_elapsed = 0         # 距上次护眼提醒的秒数

        # 休息5分钟提醒
        self._rest_break_tick = 0          # 休息后每秒计数

        self.drag_position = None

        self.init_ui()
        self.update_study_display()
        self.init_tray()
        self.set_autostart(True)
        self.setup_timer()
        # 快捷键：Ctrl+Alt+P 暂停/继续
        shortcut = QShortcut(QKeySequence('Ctrl+Alt+P'), self)
        shortcut.activated.connect(self._toggle_pause_by_shortcut)
        # 创建小浮球
        self.floating_ball = FloatingBall(self)
        # 创建5分钟倒计时浮层
        self.countdown_overlay = CountdownOverlay()
        # 20-20-20 护眼提醒
        self.eye_rest_overlay = EyeRestOverlay()

        # 启动时先定位到屏幕右侧，主窗口默认隐藏（只显示小浮球）
        self.position_to_right()
        self.hide()
        # 呼吸灯在窗口显示时才跑
        self._glow_timer.start(50)
        # 恢复上次运行状态（跨重启续接）
        self._restore_active_state()
        # 启动时提示设目标
        self._prompt_goal()

    def init_ui(self):
        self.setWindowTitle('休息提醒')
        self.widget_width = 380
        self.widget_height = 340
        self.setGeometry(100, 100, self.widget_width, self.widget_height)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
        self.app_icon = QIcon(ico_path)
        self.setWindowIcon(self.app_icon)
        self.setObjectName('mainWindow')

        # ── 全局样式 ──
        self.setStyleSheet("""
            QWidget {
                background-color: #0c0c10;
                color: #e8e6e1;
            }
            QWidget#mainWindow {
                background-color: #0c0c10;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 16px;
            }
            QLabel {
                color: #e8e6e1;
                font-size: 14px;
                background: transparent;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #555;
                border: none;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
                border-radius: 14px;
            }
            QPushButton#closeBtn:hover {
                color: #d4af37;
                background: rgba(212, 175, 55, 0.10);
            }
            QPushButton#primaryBtn {
                background-color: rgba(212, 175, 55, 0.12);
                color: #d4af37;
                border: 1px solid rgba(212, 175, 55, 0.25);
                border-radius: 10px;
                padding: 12px;
                font-family: 'Georgia, "Noto Serif SC", serif';
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#primaryBtn:hover {
                background-color: rgba(212, 175, 55, 0.22);
                border-color: #d4af37;
            }
            QPushButton#primaryBtn:disabled {
                background-color: transparent;
                color: #3a3835;
                border-color: #2a2928;
            }
            QPushButton#secondaryBtn {
                background-color: rgba(255, 122, 80, 0.06);
                color: #ff7a50;
                border: 1px solid rgba(255, 122, 80, 0.15);
                border-radius: 10px;
                padding: 12px;
                font-family: 'Georgia, "Noto Serif SC", serif';
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton#secondaryBtn:hover {
                background-color: rgba(255, 122, 80, 0.12);
                border-color: #ff7a50;
            }
            QPushButton#secondaryBtn:disabled {
                background-color: transparent;
                color: #3a3835;
                border-color: #2a2928;
            }
            QPushButton#toolBtn {
                background-color: transparent;
                color: #666;
                border: 1px solid rgba(255, 255, 255, 0.06);
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 11px;
            }
            QPushButton#toolBtn:hover {
                color: #d4af37;
                background: rgba(212, 175, 55, 0.06);
                border-color: rgba(212, 175, 55, 0.15);
            }
            QProgressBar {
                border: none;
                border-radius: 2px;
                background-color: rgba(255,255,255,0.04);
                text-align: center;
            }
            QProgressBar::chunk {
                border-radius: 2px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 14, 20, 18)
        main_layout.setSpacing(0)

        # ═══ 顶部：标题 + 关闭 ═══
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        title_label = QLabel('⚡ 精力管理')
        title_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 11, QFont.Bold))
        title_label.setStyleSheet('color: #555;')
        top_layout.addWidget(title_label)

        top_layout.addStretch()

        close_btn = QPushButton('×')
        close_btn.setObjectName('closeBtn')
        close_btn.setFixedSize(24, 24)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setToolTip('隐藏到托盘')
        close_btn.clicked.connect(self.hide)
        top_layout.addWidget(close_btn)
        main_layout.addLayout(top_layout)

        # ═══ 22:00 倒计时（大字） ═══
        main_layout.addSpacing(10)

        self.countdown_label = QLabel('⏳ 8h 30m')
        self.countdown_label.setFont(QFont('Consolas, "SF Mono", monospace', 32, QFont.Bold))
        self.countdown_label.setStyleSheet('color: #6a9bcc; letter-spacing: 2px;')
        self.countdown_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        self.countdown_bar = QProgressBar()
        self.countdown_bar.setMaximum(100)
        self.countdown_bar.setValue(100)
        self.countdown_bar.setTextVisible(False)
        self.countdown_bar.setFixedHeight(3)
        self.countdown_bar.setStyleSheet("QProgressBar { background: rgba(255,255,255,0.04); border: none; border-radius: 2px; } QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a5a8a, stop:0.5 #6a9bcc, stop:1 #8ab8e0); border-radius: 2px; }")
        main_layout.addWidget(self.countdown_bar)

        # ═══ 学习倒计时（距离休息还有多久） ═══
        main_layout.addSpacing(14)

        self.timer_label = QLabel('续航 60:00')
        self.timer_label.setFont(QFont('Consolas, "SF Mono", monospace', 18, QFont.Bold))
        self.timer_label.setStyleSheet('color: #d4af37; letter-spacing: 1px;')
        self.timer_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.timer_label)

        # ═══ 今日电脑使用时长 ═══
        main_layout.addSpacing(12)

        computer_row = QHBoxLayout()
        computer_row.setContentsMargins(4, 0, 4, 0)

        computer_icon = QLabel('💻')
        computer_icon.setFont(QFont('Segoe UI Emoji', 12))
        computer_icon.setStyleSheet('background: transparent;')
        computer_row.addWidget(computer_icon)

        self.computer_label = QLabel('今日 0h 0m')
        self.computer_label.setFont(QFont('Consolas, "SF Mono", monospace', 13))
        self.computer_label.setStyleSheet('color: #888;')
        computer_row.addWidget(self.computer_label)

        computer_row.addStretch()
        main_layout.addLayout(computer_row)

        # ═══ 开始 / 暂停 按钮 ═══
        main_layout.addSpacing(12)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)

        self.start_btn = QPushButton('▶ 开始学习')
        self.start_btn.setFont(QFont('Georgia, "Noto Serif SC", serif', 12, QFont.Bold))
        self.start_btn.setFixedHeight(40)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setObjectName('primaryBtn')
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton('⏸ 暂停')
        self.pause_btn.setFont(QFont('Georgia, "Noto Serif SC", serif', 12, QFont.Bold))
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setObjectName('secondaryBtn')
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        btn_layout.addWidget(self.pause_btn)

        main_layout.addLayout(btn_layout)

        # ═══ 底部工具按钮 ═══
        main_layout.addSpacing(10)

        tool_layout = QHBoxLayout()
        tool_layout.setSpacing(6)
        tool_layout.setContentsMargins(0, 0, 0, 0)

        for text, slot in [
            ('📊 趋势', self.show_stats),
            ('🤖 AI报告', self._show_ai_report),
            ('⚙️ 设置', self._show_settings_dialog),
        ]:
            btn = QPushButton(text)
            btn.setObjectName('toolBtn')
            btn.setFixedHeight(28)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            tool_layout.addWidget(btn)

        tool_layout.addStretch()

        # 自启按钮
        self.autostart_btn = QPushButton('🔄 自启')
        self.autostart_btn.setObjectName('toolBtn')
        self.autostart_btn.setFixedHeight(28)
        self.autostart_btn.setCursor(Qt.PointingHandCursor)
        self.autostart_btn.clicked.connect(self._toggle_autostart_btn)
        tool_layout.addWidget(self.autostart_btn)

        main_layout.addLayout(tool_layout)

        self.setLayout(main_layout)

        # ═══ 呼吸灯动画 ═══
        self._glow_opacity = 0
        self._glow_dir = 1
        self._glow_timer = QTimer(self)
        self._glow_timer.timeout.connect(self._update_glow)

        # 同步自启按钮状态
        self.autostart_btn.setText('✅ 自启' if self.is_autostart_enabled() else '🔄 自启')

    def _update_glow(self):
        """呼吸灯：运行时计时器颜色脉动"""
        if not self.timer.isActive():
            self._glow_opacity = 0
            self.timer_label.setStyleSheet('color: #d4af37; letter-spacing: 1px;')
            return
        self._glow_opacity += self._glow_dir * 2
        if self._glow_opacity >= 30:
            self._glow_dir = -1
        elif self._glow_opacity <= 0:
            self._glow_dir = 1
        o = self._glow_opacity
        r = 180 + o * 2
        g = 140 + o
        self.timer_label.setStyleSheet(
            f'color: rgb({r},{g},30); letter-spacing: 1px;')

    def show_stats(self):
        """显示趋势分析窗口（每次重建，避免 WA_DeleteOnClose 后引用失效）"""
        log.info('[show_stats] 用户点击了趋势分析')
        try:
            # 检查旧窗口是否还活着
            if hasattr(self, '_trend_window'):
                try:
                    if self._trend_window.isVisible():
                        self._trend_window.raise_()
                        self._trend_window.activateWindow()
                        return
                except (RuntimeError, Exception):
                    pass  # C++ 对象已销毁，重建
            self._trend_window = TrendWindow()
            self._trend_window.show()
            log.info('[show_stats] TrendWindow 已创建并显示')
        except Exception as e:
            import traceback
            log.error(f'[show_stats] 失败: {type(e).__name__}: {e}')
            traceback.print_exc()
            QMessageBox.warning(self, '提示', f'无法打开报告窗口: {e}')

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
        # 直接启动主程序，不经过看门狗
        script = os.path.abspath(__file__)
        pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        # WindowsApps 代理检测：避免 Store 代理导致双实例
        try:
            if 'WindowsApps' in pythonw and os.path.exists(pythonw) and os.path.getsize(pythonw) < 100_000:
                for p in os.environ.get('PATH', '').split(os.pathsep):
                    if 'WindowsApps' in p:
                        continue
                    real = os.path.join(p, 'pythonw.exe')
                    if os.path.exists(real) and os.path.getsize(real) > 100_000:
                        pythonw = real
                        break
        except Exception:
            log.error('[自启动] WindowsApps 代理检测失败')
            pass
        return f'"{pythonw}" "{script}" --silent'

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
        self._toggle_autostart_btn()

    def init_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('⚡ 精力管理 · 待开始')
        self.tray_icon.activated.connect(self._on_tray_activated)

        # 右键菜单：3 个按钮
        tray_menu = QMenu()
        action_main = QAction('🖥️  打开主界面', self)
        action_main.triggered.connect(self._tray_open_main)
        tray_menu.addAction(action_main)
        action_web = QAction('🌐  打开官方网站', self)
        action_web.triggered.connect(self._tray_open_website)
        tray_menu.addAction(action_web)
        tray_menu.addSeparator()
        action_quit = QAction('✕  退出', self)
        action_quit.triggered.connect(self.quit_app)
        tray_menu.addAction(action_quit)
        self._tray_menu = tray_menu
        self.tray_icon.setContextMenu(tray_menu)

        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.show()

    def _on_tray_activated(self, reason):
        if reason in (QSystemTrayIcon.Trigger, QSystemTrayIcon.DoubleClick):
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
                self.raise_()

    def _tray_open_main(self):
        self.show()
        self.activateWindow()
        self.raise_()

    def _tray_open_website(self):
        open_url("https://024f119c.rest-reminder-app.pages.dev/")

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
        'resting': {'start_en': False, 'start_txt': '▶ 开始', 'pause_en': False, 'pause_txt': '⏸ 暂停'},
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

    def _pause_timer(self, auto_paused=False):
        """暂停计时器（计算剩余时间）"""
        remaining = self._activity_interval * 60 - (datetime.now() - self.start_time).total_seconds()
        self.remaining_when_paused = max(remaining, 0)
        self.timer_state = 'paused'
        self._sync_buttons()

    def _resume_timer(self):
        """恢复计时器（从暂停位置继续）"""
        if self.remaining_when_paused is None:
            log.warning('[_resume_timer] remaining_when_paused is None, resetting to idle')
            self._reset_timer_to_idle()
            return
        self.start_time = datetime.now() - timedelta(seconds=(self._activity_interval * 60 - self.remaining_when_paused))
        self.remaining_when_paused = None
        self.timer_state = 'running'
        self._sync_buttons()

    def on_start_clicked(self):
        try:
            if self.timer_state not in ('idle', 'paused'):
                return
            if self.timer_state == 'idle':
                self.start_time = datetime.now()
                self._activity_interval = 60
            else:
                log.info(f'[on_start_clicked] 用户点击继续（剩余{int(self.remaining_when_paused//60)}分{int(self.remaining_when_paused%60)}秒）')
                self._resume_timer()
                return
            self.timer_state = 'running'
            self._sync_buttons()
        except Exception as e:
            log.error(f'[on_start_clicked 异常] {type(e).__name__}: {e}')

    def on_pause_clicked(self):
        try:
            if self.timer_state != 'running':
                return
            self._pause_timer()
        except Exception as e:
            log.error(f'[on_pause_clicked 异常] {type(e).__name__}: {e}')

    def _toggle_pause_by_shortcut(self):
        """快捷键切换暂停/继续"""
        try:
            if self.timer_state == 'running':
                self._pause_timer()
                self.tray_icon.showMessage('⏸ 已暂停', '计时器已暂停', QSystemTrayIcon.Information, 1500)
            elif self.timer_state == 'paused':
                self._resume_timer()
                self.tray_icon.showMessage('▶ 已继续', '计时器已继续', QSystemTrayIcon.Information, 1500)
        except Exception as e:
            log.error(f'[_toggle_pause_by_shortcut 异常] {type(e).__name__}: {e}')

    def _reset_timer_to_idle(self):
        try:
            self.timer_state = 'idle'
            self.start_time = None
            self.remaining_when_paused = None
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()
            self._sync_buttons()
        except Exception as e:
            log.error(f'[_reset_timer_to_idle 异常] {type(e).__name__}: {e}')

    def _handle_idle(self):
        """处理空闲状态 - 显示默认时间或休息中"""
        if self.break_start is not None:
            # 休息中，实时显示休息时长
            elapsed_mins = (datetime.now() - self.break_start).total_seconds() / 60
            self.timer_label.setText(f'☕ {int(elapsed_mins)}m')
            self._update_break_display()
            self.tray_icon.setToolTip(f'⚡ 精力管理 · ☕ 休息中 {int(elapsed_mins)}m')
        else:
            self.timer_label.setText(f'续航 {self._activity_interval:02d}:00')
            self.tray_icon.setToolTip(f'⚡ 精力管理 · 续航 {self._activity_interval}min')

    def _handle_running(self, now):
        """处理运行状态 - 固定60分钟倒计时 -> 5分钟请辨 -> 5分钟休息"""
        elapsed = (now - self.start_time).total_seconds()
        total_seconds = 60 * 60  # 固定60分钟
        remaining = max(total_seconds - elapsed, 0)

        mins = int(remaining // 60)
        secs = int(remaining % 60)
        self.timer_label.setText(f'\u26a1 {mins:02d}:{secs:02d}')
        self.tray_icon.setToolTip(f'\u26a1 精力管理 · 剩余 {mins}:{secs:02d}')

        # 最后5分钟倒计时浮层
        if remaining <= 300 and remaining > 0 and not self._study_countdown_active:
            self._study_countdown_active = True
            quote, tag = _pick_quote()
            self.countdown_overlay.show_countdown(
                remaining, '\ud83d\udcda 学习即将结束', quote, total_seconds=300
            )

        if remaining > 300 and self._study_countdown_active:
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()

        # 倒计时结束 -> 进入休息状态
        if remaining <= 0:
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()
            self.timer_state = 'resting'
            self._rest_start_time = now
            self._rest_end_time = now + timedelta(minutes=5)
            self._pending_review = True
            self._prompt_review()
            self._sync_buttons()
            log.info('[计时] 学习60分钟结束，进入5分钟休息')


    def _handle_resting(self, now):
        """处理休息状态 - 5分钟休息倒计时"""
        if now >= self._rest_end_time:
            # 休息结束
            self._round_count += 1
            study_add = 1.0
            self.study_hours_today = round(self.study_hours_today + study_add, 2)
            self.update_study_display()
            LocalSync.increment_study_hour(self.study_hours_today)
            log.info(f'[计时] 休息结束，第{self._round_count}轮完成')

            # 每3轮后（第3、6、9...轮）打开护眼视频，否则打开收藏夹
            if self._round_count % 3 == 0:
                eye_url = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click'
                open_url(eye_url)
                self.tray_icon.showMessage(
                    '👁️ 护眼时间',
                    '每3轮休息，看看护眼视频放松眼睛~',
                    QSystemTrayIcon.Information,
                    4000
                )
            else:
                fav_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create&spm_id_from=333.788.0.0'
                open_url(fav_url)

            self.break_start = None
            self.timer_state = 'idle'
            self._sync_buttons()
            self.tray_icon.showMessage(
                '▶ 下一轮',
                '休息结束，准备开始下一轮学习~',
                QSystemTrayIcon.Information,
                3000
            )
        else:
            # 显示休息倒计时
            remaining = (self._rest_end_time - now).total_seconds()
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            self.timer_label.setText(f'☕ {mins:02d}:{secs:02d}')
            self.tray_icon.setToolTip(f'⚡ 精力管理 · 休息中 {mins}:{secs:02d}')

    def _handle_paused(self, now):
        """处理暂停状态 - 显示暂停时间"""
        if self.remaining_when_paused is None:
            self.timer_label.setText('⏸ 已暂停')
            self.tray_icon.setToolTip('⚡ 精力管理 · ⏸ 已暂停')
            return
        mins = int(self.remaining_when_paused // 60)
        secs = int(self.remaining_when_paused % 60)
        self.timer_label.setText(f'⏸ 已暂停：{mins:02d}:{secs:02d}')
        self.tray_icon.setToolTip(f'⚡ 精力管理 · ⏸ 剩余 {mins}:{secs:02d}')
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

        self.countdown_label.setText(f'⏳ {hours}h {minutes:02d}m')

        # 进度条从0点(100%)到22:00(0%)倒计时模式
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        if now.hour >= 22:
            midnight = midnight + timedelta(days=1)
        seconds_since_midnight = (now - midnight).total_seconds()
        progress = 100 - int((seconds_since_midnight / (22 * 3600)) * 100)
        self.countdown_bar.setValue(max(progress, 0))

        # 22:00 每日汇报提醒（每天只弹一次）
        if now.hour >= 22 and not self._daily_report_shown_today:
            self._daily_report_shown_today = True
            study = self.study_hours_today
            msg = (f'今日学习：{study} 小时\n\n')

            # 加入复盘总结
            reviews_data = review_store.load()
            today_reviews = reviews_data.get(datetime.now().date().isoformat(), [])
            if today_reviews:
                scores = [e['score'] for e in today_reviews]
                avg = sum(scores) / len(scores)
                msg += f'📊 复盘 {len(scores)} 次 · 平均 {avg:.1f}⭐\n'
                # 最佳/最差时段
                best = max(today_reviews, key=lambda e: e['score'])
                worst = min(today_reviews, key=lambda e: e['score'])
                msg += f'🏆 最佳: {best["time"]}({best["score"]}⭐) · ⚠️ 待改进: {worst["time"]}({worst["score"]}⭐)\n'
                # 昨日对比
                yesterday_avg = self._load_yesterday_review_avg(reviews_data)
                if yesterday_avg is not None:
                    diff = avg - yesterday_avg
                    arrow = '📈' if diff > 0 else '📉' if diff < 0 else '➡️'
                    msg += f'{arrow} 比昨日 {("+" if diff>0 else "")}{diff:.2f}⭐\n'
            else:
                msg += '📝 今天还没有复盘记录\n'

            msg += '\n记得记录到飞书～'
            self.tray_icon.showMessage('📋 每日记录提醒', msg, QSystemTrayIcon.Information, 8000)
            log.info(f'[DailyReport] 22:00 提醒: 学习{study}h, 电脑{computer:.1f}h')
            # 检查连续打卡
            self._check_streak()

    def _load_yesterday_review_avg(self, reviews_data=None):
        """加载昨日平均评分"""
        if reviews_data is None:
            reviews_data = review_store.load()
        yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
        entries = reviews_data.get(yesterday, [])
        if entries:
            scores = [e['score'] for e in entries]
            return sum(scores) / len(scores)
        return None

    def update_display(self):
        try:
            now = datetime.now()

            # --- 日期变化重置 ---
            if now.date() != self.current_date:
                # 日期变化前检查昨天的打卡
                self._check_streak()
                # 重置数据
                self.played_today = set()
                self.study_hours_today = 0
                self.computer_usage_ticks = 0
                self._round_count = 0
                self._activity_interval = 60
                self.break_start = None
                self._rest_break_tick = 0
                self._study_countdown_active = False
                self.countdown_overlay.hide_overlay()
                self.current_date = now.date()
                self._daily_report_shown_today = False
                self._bilibili_dns_error_logged = False
                LocalSync.reset()
                self.break_minutes_today = 0
                LocalSync.save_break_minutes(0)
                self._save_computer_usage()
                self.update_study_display()
                log.info(f'新的一天，数据已重置: {self.current_date}')


            # --- 状态机路由 ---
            if self.timer_state == 'idle':
                self._handle_idle()
            elif self.timer_state == 'running':
                self._handle_running(now)
            elif self.timer_state == 'resting':
                self._handle_resting(now)
            elif self.timer_state == 'paused':
                self._handle_paused(now)

            # --- 22:00 倒计时（统一更新，避免重复请求） ---
            self._update_countdown(now)

            # --- 每 15 秒电池检测 ---
            self._battery_tick += 1
            if self._battery_tick >= 15:
                self._battery_tick = 0
                self.update_battery_status()

            # --- 每5分钟保存历史统计 ---
            self._stats_tick += 1
            if self._stats_tick >= 300:
                self._stats_tick = 0
                LocalSync.save_daily_stats()

            # --- 每30秒保存运行状态（防崩溃丢失） ---
            self._state_save_tick += 1
            if self._state_save_tick >= 30:
                self._state_save_tick = 0
                self._save_active_state()

            # --- 电脑使用时长简单累计 ---
            self.update_computer_usage(now)

        except Exception as e:
            log.error(f'[update_display 异常] {type(e).__name__}: {e}')
            traceback.print_exc()

    def update_study_display(self):
        """更新电脑使用时长显示"""
        total_h = int(self.computer_usage_hours_today)
        total_m = int((self.computer_usage_hours_today - total_h) * 60)
        self.computer_label.setText(f'今日 {total_h}h {total_m}m')

    def _update_break_display(self):
        """休息时长在 _handle_idle 的 timer_label 中实时显示"""
        pass
    def _build_review_dialog(parent, title, label):
        """构建复盘评分对话框（共享 UI 代码）"""
        scores = ['1⭐ 摸鱼', '2⭐ 一般', '3⭐ 还行', '4⭐ 不错', '5⭐ 专注']
        dialog = QInputDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setLabelText(label)
        dialog.setComboBoxItems(scores)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        QTimer.singleShot(30000, dialog.close)  # 30秒自动关闭
        return dialog

    def _prompt_review(self):
        """快速复盘弹窗：这小时产出自评（非阻塞，30秒自动关闭）"""
        try:
            if not self._pending_review:
                return
            dialog = self._build_review_dialog(self, '快速复盘', '这小时产出怎么样？')
            if dialog.exec_():
                score_str = dialog.textValue()
                if score_str:
                    score = int(score_str[0])
                    self._record_review(score)
        except Exception as e:
            log.error(f'[复盘] 弹窗异常: {e}')

    def _record_review(self, score):
        """记录自评分数（持久化到 .review_log.json）"""
        if not self._pending_review:
            return
        self._pending_review = False
        log.info(f'[复盘] 本周期评分: {score}/5')
        self._write_review(score)

    def _catchup_review(self):
        """补录复盘：托盘菜单入口"""
        dialog = self._build_review_dialog(self, '📝 补录复盘', '刚才（漏掉的）那小时产出怎么样？')
        if dialog.exec_():
            score_str = dialog.textValue()
            if score_str:
                score = int(score_str[0])
                self._write_review(score)
                self.tray_icon.showMessage('📝 已补录', f'已记录复盘：{score}⭐', QSystemTrayIcon.Information, 2000)

    def _write_review(self, score):
        """写入复盘记录到文件（供正常复盘和补录共用）"""
        try:
            data = review_store.load()
            today = datetime.now().date().isoformat()
            if today not in data:
                data[today] = []
            data[today].append({
                'time': datetime.now().strftime('%H:%M'),
                'score': score
            })
            review_store.save(data)
            log.info(f'[复盘] 已记录: {score}/5')
        except Exception as e:
            log.error(f'[复盘] 保存失败: {e}')

    def _prompt_goal(self):
        """启动时弹出目标选择"""
        if self.goal_text:
            return
        try:
            self._show_goal_dialog()
        except Exception as e:
            log.error(f'[目标] 提示异常: {e}')

    def _show_goal_dialog(self, event=None):
        """显示目标选择对话框（event 参数用于 mousePressEvent 回调）"""
        try:
            goals = _GOAL_OPTIONS
            goal, ok = QInputDialog.getItem(self, '设定今日目标', '今天主要做什么？', goals, 0, False)
            if ok and goal:
                self.goal_text = goal
                goal_store.save({'date': datetime.now().date().isoformat(), 'goal': goal})
                self.update_study_display()
                log.info(f'[目标] 设定为: {goal}')
        except Exception as e:
            log.error(f'[目标] 对话框异常: {e}')

    def _show_eye_rest_reminder(self):
        # 20-20-20 护眼提醒：每20分钟弹出，15秒自动消失
        if self.timer_state in ('idle',):
            return
        self.eye_rest_overlay.show_reminder()
        log.info('[护眼] 20-20-20 提醒触发')

    def _reset_eye_rest(self):
        # 重置护眼计时（休息/暂停时重置）
        self.eye_rest_elapsed = 0

    def _set_reminder_mode(self, mode):
        """设置提醒方式"""
        self.app_settings['reminder_mode'] = mode
        LocalSync.save_settings(self.app_settings)
        mode_names = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '只弹通知', 'none': '无操作'}
        self.tray_icon.showMessage('提醒方式', f'已切换为：{mode_names.get(mode, mode)}', QSystemTrayIcon.Information, 2000)
        log.info(f'[设置] 提醒方式切换为: {mode}')

    def _show_settings_dialog(self):
        """设置对话框：提醒方式 + B站收藏夹 + 测试连接"""
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QLabel, QComboBox,
                                     QLineEdit, QPushButton, QHBoxLayout, QMessageBox)
        dialog = QDialog(self)
        dialog.setWindowTitle('⚙️ 设置')
        dialog.setFixedSize(360, 400)
        dialog.setStyleSheet("""
            QDialog { background-color: #141413; color: #faf9f5; border-radius: 12px; }
            QLabel { color: #e8e6e1; font-size: 12px; }
            QComboBox { background: #1e1d1b; color: #e8e6e1; border: 1px solid #333; border-radius: 6px; padding: 6px; font-size: 12px; }
            QLineEdit { background: #1e1d1b; color: #e8e6e1; border: 1px solid #333; border-radius: 6px; padding: 6px; font-size: 12px; }
            QPushButton { background: rgba(212,175,55,0.12); color: #d4af37; border: 1px solid rgba(212,175,55,0.2); border-radius: 100px; padding: 8px; font-size: 11px; }
            QPushButton:hover { background: rgba(212,175,55,0.2); }
            QPushButton#testBtn { background: rgba(120,180,80,0.12); color: #78B450; border: 1px solid rgba(120,180,80,0.2); }
            QPushButton#testBtn:hover { background: rgba(120,180,80,0.2); }
        """)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(8)

        layout.addWidget(QLabel('📢 提醒方式'))
        mode_combo = QComboBox()
        mode_combo.addItems(['打开B站', '💡 请辨金句', '只弹通知', '无操作'])
        mode_map = {'打开B站': 'video', '💡 请辨金句': 'quote', '只弹通知': 'notify', '无操作': 'none'}
        current_mode = self.app_settings.get('reminder_mode', 'video')
        for i, (k, v) in enumerate(mode_map.items()):
            if v == current_mode:
                mode_combo.setCurrentIndex(i)
                break
        layout.addWidget(mode_combo)

        layout.addWidget(QLabel('🎬 B站收藏夹 ID'))
        fid_input = QLineEdit()
        fid_input.setText(self.app_settings.get('bilibili_fid', '3648313921'))
        fid_input.setPlaceholderText('收藏夹 media_id')
        layout.addWidget(fid_input)

        layout.addWidget(QLabel('👤 B站用户 ID'))
        mid_input = QLineEdit()
        mid_input.setText(self.app_settings.get('bilibili_mid', '529362421'))
        mid_input.setPlaceholderText('用户 mid')
        layout.addWidget(mid_input)

        test_btn = QPushButton('🔍 测试收藏夹连接')
        test_btn.setObjectName('testBtn')
        layout.addWidget(test_btn)
        test_result = QLabel('')
        test_result.setStyleSheet('font-size: 11px; background: transparent;')
        layout.addWidget(test_result)

        def _set_result(text, color):
            test_result.setText(text)
            test_result.setStyleSheet(f'color: {color}; font-size: 11px; background: transparent;')
            test_btn.setText('🔍 测试收藏夹连接')
            test_btn.setEnabled(True)

        def test_bilibili():
            fid = fid_input.text().strip()
            if not fid:
                _set_result('⚠️ 请先填写收藏夹 ID', '#ff8844')
                return
            test_btn.setEnabled(False)
            test_btn.setText('测试中...')
            QApplication.processEvents()
            import threading
            def _do_test():
                try:
                    import requests
                    url = f'https://api.bilibili.com/x/v3/fav/folder/info?media_id={fid}'
                    h = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.bilibili.com'}
                    try:
                        r = requests.get(url, headers=h, timeout=5)
                        data = r.json()
                        code = data.get('code', -1)
                    except requests.Timeout:
                        QTimer.singleShot(0, lambda: _set_result('⚠️ 网络超时', '#ff8844'))
                        return
                    except requests.ConnectionError:
                        QTimer.singleShot(0, lambda: _set_result('⚠️ 无法连接B站API', '#ff8844'))
                        return
                    if code == 0:
                        d = data.get('data', {})
                        QTimer.singleShot(0, lambda: _set_result(f'✅ 收藏夹「{d.get("title","?")}」· {d.get("media_count",0)} 个视频', '#78B450'))
                    elif code == -400:
                        QTimer.singleShot(0, lambda: _set_result('❌ 收藏夹不存在', '#ff4444'))
                    else:
                        QTimer.singleShot(0, lambda: _set_result(f'⚠️ API 错误 ({code})', '#ff8844'))
                except Exception as e:
                    QTimer.singleShot(0, lambda: _set_result(f'❌ 错误: {str(e)[:30]}', '#ff4444'))
            threading.Thread(target=_do_test, daemon=True).start()

        test_btn.clicked.connect(test_bilibili)
        layout.addSpacing(6)

        btn_row = QHBoxLayout()
        save_btn = QPushButton('保存')
        close_btn = QPushButton('关闭')
        btn_row.addWidget(save_btn)
        btn_row.addWidget(close_btn)
        layout.addLayout(btn_row)

        def save_settings():
            self.app_settings['reminder_mode'] = mode_map.get(mode_combo.currentText(), 'video')
            self.app_settings['bilibili_fid'] = fid_input.text().strip()
            self.app_settings['bilibili_mid'] = mid_input.text().strip()
            LocalSync.save_settings(self.app_settings)
            mode_names = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '只弹通知', 'none': '无操作'}
            self.tray_icon.showMessage('设置', '设置已保存', QSystemTrayIcon.Information, 1500)
            log.info(f'[设置] 提醒方式切换为: {self.app_settings["reminder_mode"]}')
            dialog.close()

        save_btn.clicked.connect(save_settings)
        close_btn.clicked.connect(dialog.close)
        dialog.exec_()

    def _toggle_autostart_btn(self):
        new_state = not self.is_autostart_enabled()
        if self.set_autostart(new_state):
            tip = '已开启' if new_state else '已关闭'
            self.autostart_btn.setText('✅ 自启' if new_state else '🔄 自启')
            self.tray_icon.showMessage('休息提醒', f'开机自启动{tip}', QSystemTrayIcon.Information, 2000)

    def _show_ai_report(self):
        """显示 AI 学习分析报告"""
        try:
            from pro_features import generate_report
        except ImportError:
            QMessageBox.information(self, '🤖 AI 报告',
                'AI 模块加载失败，请检查 rest-reminder-pro/ 目录是否存在。')
            return

        # 选择报告类型
        from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                                     QPushButton, QTextBrowser, QLabel, QMessageBox)
        dialog = QDialog(self)
        dialog.setWindowTitle('🤖 AI 学习报告')
        dialog.setFixedSize(600, 500)
        dialog.setStyleSheet("""
            QDialog { background-color: #0c0c10; color: #e8e6e1; }
            QTextBrowser { background: #14141a; color: #e8e6e1; border: 1px solid #222; border-radius: 8px; padding: 12px; font-size: 13px; }
            QPushButton { background: rgba(212,175,55,0.12); color: #d4af37; border: 1px solid rgba(212,175,55,0.2); border-radius: 100px; padding: 8px 16px; font-size: 11px; }
            QPushButton:hover { background: rgba(212,175,55,0.2); }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        layout.addWidget(QLabel('选择报告类型：'))

        type_btns = QHBoxLayout()
        types = [('日报', 'daily'), ('周报', 'weekly'), ('月报', 'monthly'),
                 ('季报', 'quarterly'), ('年报', 'yearly')]
        report_view = QTextBrowser()
        report_view.setOpenExternalLinks(True)

        def fetch_report(report_type, label):
            # 先请求缓存
            result = generate_report(report_type, force_refresh=False)
            if result.get("ok"):
                report_view.setPlainText(result['content'])
            elif result.get("error"):
                report_view.setPlainText(f'⚠️ AI 请求失败: {result["error"]}\n\n点击「刷新」重试。')
            else:
                report_view.setPlainText('⏳ 正在生成报告...\n\nAI 分析中，请稍候...')

        # 类型按钮 — 用 *args 吸收 clicked 信号的 bool 参数
        for label, rtype in types:
            btn = QPushButton(label)
            def _on_type(*args, t=rtype, l=label):
                _current_type['type'] = t
                fetch_report(t, l)
            btn.clicked.connect(_on_type)
            type_btns.addWidget(btn)

        layout.addLayout(type_btns)
        layout.addWidget(report_view)

        # 刷新按钮 — 刷新当前选中类型
        refresh_btn = QPushButton('🔄 刷新')
        _current_type = {'type': 'daily'}

        def do_refresh():
            fetch_report(_current_type['type'],
                         {'daily': '日报', 'weekly': '周报', 'monthly': '月报',
                          'quarterly': '季报', 'yearly': '年报'}.get(_current_type['type'], '日报'))

        refresh_btn.clicked.connect(do_refresh)
        layout.addWidget(refresh_btn)

        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)

        # 默认显示日报
        fetch_report('daily', '日报')
        dialog.exec_()

    def _restore_active_state(self):
        """启动时恢复上次运行状态（跨重启续接）"""
        state = LocalSync.load_app_state()
        if state is None:
            return

        # 休息时长：app_state 是绝对值（最新），优先于 daily_log
        self.break_minutes_today = state.get('break_minutes', self.break_minutes_today)

        # 恢复活动感知间隔
        saved_interval = state.get('activity_interval')
        if saved_interval and saved_interval in (45, 60):
            self._activity_interval = saved_interval
        # 计时器状态恢复
        saved_state = state.get('timer_state')
        if saved_state == 'running':
            saved_remaining = state.get('remaining', 0)
            if saved_remaining > 0 and saved_remaining < self._activity_interval * 60:
                self.start_time = datetime.now() - timedelta(seconds=(self._activity_interval * 60 - saved_remaining))
                self.timer_state = 'running'
                self._sync_buttons()
                log.info(f'[恢复] 续接倒计时，剩余 {int(saved_remaining//60)} 分 {int(saved_remaining%60)} 秒')
            else:
                # 倒计时已过期，直接进入休息
                self.break_start = datetime.now()
                self.timer_state = 'idle'
                self._sync_buttons()
                log.info('[恢复] 倒计时已过期，直接进入休息')
        elif saved_state == 'paused':
            self.remaining_when_paused = state.get('remaining', 0)
            self.timer_state = 'paused'
            self._sync_buttons()
            log.info(f'[恢复] 暂停状态，剩余 {int(self.remaining_when_paused//60)} 分 {int(self.remaining_when_paused%60)} 秒')

        # 恢复休息开始时间（仅限今天，忽略跨天的过期数据）
        if self.break_start is None and state.get('break_start'):
            try:
                bs = datetime.fromisoformat(state['break_start'])
                if bs.date() == datetime.now().date():
                    self.break_start = bs
            except Exception as e:
                log.warning(f'[恢复] break_start 解析失败: {e}')

        self.played_today = set(state.get('played_today', []))
        self._round_count = state.get('round_count', 0)
        self.update_study_display()

    def _save_active_state(self):
        """保存当前运行状态到本地文件（防崩溃丢失）"""
        remaining = 0
        if self.timer_state == 'running' and self.start_time:
            remaining = max(self._activity_interval * 60 - (datetime.now() - self.start_time).total_seconds(), 0)
        elif self.timer_state == 'paused' and self.remaining_when_paused is not None:
            remaining = self.remaining_when_paused

        state = {
            'timer_state': self.timer_state,
            'remaining': round(remaining),
            'break_start': self.break_start.isoformat() if self.break_start else None,
            'break_minutes': self.break_minutes_today,
            'played_today': list(self.played_today),
            'activity_interval': self._activity_interval,
            'round_count': self._round_count,
        }
        LocalSync.save_app_state(state)

    def _check_streak(self):
        """检查今日打卡 + 从历史数据自动恢复被清零的连续打卡"""
        today = datetime.now().date().isoformat()
        streak = self.streak_data

        # 没达标就不需要查历史
        if self.study_hours_today < STREAK_THRESHOLD_HOURS:
            self.streak_data = streak
            LocalSync.save_streak(streak)
            self._update_streak_display()
            return

        # 如果 streak 被清零但历史数据显示昨天达标，自动恢复
        if streak['current_streak'] == 0 and streak.get('best_streak', 0) > 0:
            yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
            hist = history_store.load()
            y_data = hist.get(yesterday, {})
            y_study = y_data.get('study', 0) if isinstance(y_data, dict) else 0
            if y_study >= STREAK_THRESHOLD_HOURS:
                streak['current_streak'] = 1
                streak['last_streak_date'] = yesterday
                log.info(f'[打卡] 从历史恢复：昨日{y_study}h >= {STREAK_THRESHOLD_HOURS}h，连续 {streak["current_streak"]} 天')

        if streak.get('last_streak_date') != today:
            streak['current_streak'] = streak.get('current_streak', 0) + 1
            streak['last_streak_date'] = today
            if streak['current_streak'] > streak.get('best_streak', 0):
                streak['best_streak'] = streak['current_streak']
            log.info(f'[打卡] 今日学习{self.study_hours_today}h >= {STREAK_THRESHOLD_HOURS}h，连续打卡 {streak["current_streak"]} 天')
            # 里程碑金句
            milestone = _get_streak_milestone(streak['current_streak'])
            if milestone:
                msg, sub = milestone
                self.tray_icon.showMessage(
                    f'🏆 连续打卡 {streak["current_streak"]} 天！',
                    f'「{msg}」\n——{sub}',
                    QSystemTrayIcon.Information,
                    6000
                )
                log.info(f'[打卡里程碑] 第{streak["current_streak"]}天: {msg}')
        self.streak_data = streak
        LocalSync.save_streak(streak)
        self._update_streak_display()

    def _update_streak_display(self):
        """打卡数据后台追踪，主界面不再显示"""
        pass
    def export_weekly_data(self):
        """导出最近7天数据到剪贴板"""
        history = LocalSync.load_weekly_stats()
        today = datetime.now().date()
        lines = ['日期        | 学习(h) | 电脑(h) | 休息(min)']
        lines.append('-' * 42)
        total_study = 0
        total_computer = 0
        total_break = 0
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            label = (today - timedelta(days=i)).strftime('%m/%d (%a)')
            data = history.get(d, {'study': 0, 'computer': 0, 'break_minutes': 0})
            study = data.get('study', 0)
            computer = data.get('computer', 0)
            brk = data.get('break_minutes', 0)
            total_study += study
            total_computer += computer
            total_break += brk
            lines.append(f'{label}  |  {study:>5.1f}  |  {computer:>5.1f}  |  {brk:>6.1f}')
        lines.append('-' * 42)
        lines.append(f'合计        |  {total_study:>5.1f}  |  {total_computer:>5.1f}  |  {total_break:>6.1f}')
        text = '\n'.join(lines)
        QApplication.clipboard().setText(text)
        self.tray_icon.showMessage('📋 已复制到剪贴板', f'最近7天数据已导出\n\n{text}', QSystemTrayIcon.Information, 5000)
        log.info(f'[导出] 本周数据已复制到剪贴板')

    def _load_computer_usage(self):
        """从本地文件恢复今天的电脑使用计数（跨重启持久化）"""
        try:
            data = computer_store.load()
            if not data:
                return
            if data.get('date') == self.current_date.isoformat():
                self.computer_usage_ticks = int(data.get('ticks', 0))
                log.info(f'[ComputerUsage] 恢复今日计数: {self.computer_usage_ticks / 3600:.2f}h')
        except Exception as e:
            log.error(f'[ComputerUsage] 加载缓存失败: {e}')

    def _save_computer_usage(self):
        """保存当前电脑使用计数到本地文件"""
        try:
            computer_store.save({
                'date': self.current_date.isoformat(),
                'ticks': self.computer_usage_ticks
            })
        except Exception as e:
            log.error(f'[ComputerUsage] 保存缓存失败: {e}')

    def update_computer_usage(self, now):
        """更新电脑使用时长（简单累计）"""
        self.computer_usage_ticks += 1
        # 每2分钟保存一次
        self._computer_save_tick += 1
        if self._computer_save_tick >= 120:
            self._computer_save_tick = 0
            self._save_computer_usage()


    def update_battery_status(self):
        try:
            battery = psutil.sensors_battery()

            if battery is None:
                return

            percent = battery.percent
            plugged = battery.power_plugged




            if plugged:
                if percent >= 100:
                    icon, status = '🔌', '已充满'
                else:
                    icon, status = '⚡', '充电中'

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

                if self.last_charging_state is True and not plugged:
                    if not self.battery_warning_shown:
                        self.show_battery_warning(percent)
                        self.battery_warning_shown = True
                        self.battery_notification_active = True

            self.last_charging_state = plugged

        except Exception as e:
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

    def hideEvent(self, event):
        self._glow_timer.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        try:
            event.ignore()
            self._save_active_state()
            self._glow_timer.stop()
            self.hide_to_edge()
        except Exception as e:
            log.error(f'[closeEvent 异常] {type(e).__name__}: {e}')

    def quit_app(self):
        try:
            self._save_active_state()
            self._save_computer_usage()
            self.timer.stop()
            self.tray_icon.hide()
            QApplication.quit()
        except Exception as e:
            log.error(f'[quit_app 异常] {type(e).__name__}: {e}')


_single_instance = SingleInstanceChecker()


def main():
    if _single_instance.is_already_running():
        log.warning('休息提醒程序已经在运行中！')
        if '--silent' not in sys.argv:
            a = QApplication(sys.argv)
            QMessageBox.warning(None, '已在运行', '程序已在运行中！\n请检查系统托盘图标。')
        sys.exit(0)

    # 全局异常处理器
    def excepthook(exc_type, exc_value, exc_tb):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        sys.exit(1)  # 异常退出，让 atexit 清理
    sys.excepthook = excepthook

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        log.error("[DPIAware] 设置失败")
        pass

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    silent = '--silent' in sys.argv
    widget = RestReminderWidget(silent_start=silent)
    if silent:
        widget.hide()
    else:
        widget.show()

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
