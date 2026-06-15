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
import requests
import ctypes
import json
import os
import tempfile
import re
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox, QShortcut, QInputDialog, QFrame)
from PyQt5.QtCore import QTimer, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon, QFont, QCursor, QPainter, QColor, QBrush, QPen, QKeySequence, QPainterPath
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import psutil
import atexit
import winreg
import traceback
import winsound
import math
import logging
from logging.handlers import RotatingFileHandler

# 自定义托盘卡片
from tray_card import TrayCardWidget

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

STREAK_MILESTONE = {
    1:    ("耐心本身就是门槛", "大部分人在你今天就开始累积了"),
    3:    ("门槛前竞争", "3天——抢门槛的人已经甩开一批了"),
    7:    ("复利游戏", "7天——复利开始滚动"),
    14:   ("反馈密度", "14天——你已经超过了大多数人的坚持极限"),
    30:   ("门槛前竞争——耐心是真正的护城河", "30天——你不是临时起意，你是认真的"),
    60:   ("习惯即命运", "60天——这已经是生活方式了"),
    90:   ("你不需要跑得最快", "90天——只需要比躺平党快"),
    365:  ("长期主义", "365天——你已经不是一年前的你了"),
}

_GOAL_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.goal.json')
_QUOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.wisdom_quotes.json')
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
        return 0


def _load_goal():
    """读取今日目标"""
    path = _GOAL_FILE
    today = datetime.now().date().isoformat()
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                d = json.load(f)
            if d.get('date') == today:
                return d.get('goal', '')
        except Exception:
            pass
    return None


def _save_goal(goal):
    """保存今日目标"""
    with open(_GOAL_FILE, 'w', encoding='utf-8') as f:
        json.dump({'date': datetime.now().date().isoformat(), 'goal': goal}, f, ensure_ascii=False)


def _load_quotes_used():
    path = _QUOTES_FILE
    if os.path.exists(path):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return []


def _save_quotes_used(used):
    with open(_QUOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(used, f)


def _pick_quote():
    """从金句库中选一条未在今天展示过的"""
    used = _load_quotes_used()
    available = [q for q in WISDOM_QUOTES if q[0] not in used]
    if not available:
        used.clear()
        available = list(WISDOM_QUOTES)
    picked = random.choice(available)
    used.append(picked[0])
    _save_quotes_used(used)
    return picked


def _get_streak_milestone(streak):
    """获取打卡里程碑对应的金句（dict插入顺序=键升序）"""
    for k in reversed(list(STREAK_MILESTONE)):
        if streak >= k:
            return STREAK_MILESTONE[k]
    return None


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



class LocalSync:
    """本地存储学习/电脑使用时长（替代飞书同步）"""

    _data = None
    _current_date = None

    @classmethod
    def _get_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.daily_log.json')

    @classmethod
    def _load(cls):
        today = datetime.now().date().isoformat()
        if cls._data is not None and cls._current_date == today:
            return cls._data
        path = cls._get_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('date') == today:
                    cls._data = data
                    cls._current_date = today
                    return cls._data
            except Exception:
                pass
        cls._data = {'date': today, 'study_hours': 0, 'computer_hours': 0, 'break_minutes_today': 0}
        cls._current_date = today
        return cls._data

    @classmethod
    def _save(cls):
        path = cls._get_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(cls._data, f, ensure_ascii=False)

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
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.settings.json')

    @classmethod
    def load_settings(cls):
        path = cls._get_settings_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'reminder_mode': 'video'}  # 默认：打开B站

    @classmethod
    def save_settings(cls, settings):
        path = cls._get_settings_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False)
        log.info(f'[LocalSync] 设置已保存: {settings}')

    # --- 连续打卡 (.streak.json) ---
    @classmethod
    def _get_streak_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.streak.json')

    @classmethod
    def load_streak(cls):
        path = cls._get_streak_path()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {'current_streak': 0, 'last_streak_date': '', 'best_streak': 0}

    @classmethod
    def save_streak(cls, streak_data):
        path = cls._get_streak_path()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(streak_data, f, ensure_ascii=False)
        log.info(f'[LocalSync] 打卡记录: 连续{streak_data["current_streak"]}天, 最佳{streak_data["best_streak"]}天')

    @classmethod
    def _get_history_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.stats_history.json')

    @classmethod
    def save_daily_stats(cls):
        """保存今日数据到历史记录（每次调用都更新今日数据）"""
        data = cls._load()
        today = datetime.now().date().isoformat()
        path = cls._get_history_path()
        history = {}
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    history = json.load(f)
            except Exception:
                history = {}
        history[today] = {
            'study': round(data.get('study_hours', 0), 1),
            'computer': round(data.get('computer_hours', 0), 1),
            'break_minutes': round(data.get('break_minutes_today', 0), 1)
        }
        # 只保留30天
        dates = sorted(history.keys())
        if len(dates) > 30:
            for old in dates[:len(dates) - 30]:
                del history[old]
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False)

    @classmethod
    def load_weekly_stats(cls):
        """加载最近7天的统计数据"""
        path = cls._get_history_path()
        if not os.path.exists(path):
            return {}
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    @classmethod
    def reset(cls):
        cls._data = None
        cls._current_date = None

    # --- 应用状态 (.app_state.json) ---
    @classmethod
    def _get_app_state_path(cls):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), '.app_state.json')

    @classmethod
    def load_app_state(cls):
        """加载今日应用状态（计时器、休息、播放记录）"""
        path = cls._get_app_state_path()
        today = datetime.now().date().isoformat()
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                if data.get('date') == today:
                    return data
            except Exception:
                pass
        return None

    @classmethod
    def save_app_state(cls, state):
        """保存应用状态"""
        path = cls._get_app_state_path()
        state['date'] = datetime.now().date().isoformat()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False)


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
            if self._POS_FILE and os.path.exists(self._POS_FILE):
                with open(self._POS_FILE, 'r') as f:
                    pos = json.load(f)
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
            self._saved_pos = None

    def _save_position(self):
        try:
            pos = self.frameGeometry().topLeft()
            with open(self._POS_FILE, 'w') as f:
                json.dump({'x': pos.x(), 'y': pos.y()}, f)
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
        self.progress_bar.setValue(max(pct, 0))

        if self._remaining <= 60 and self._remaining > 0:
            phase = math.sin(time.time() * 4)
            font_size = int(44 + phase * 5)
            color = '#FF4A20' if phase > 0 else '#FF2200'
            self.timer_label.setStyleSheet(
                f'color: {color}; font-size: {font_size}px; font-weight: bold; font-family: Consolas; background: transparent; border: none;'
            )
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
        self.start_time = None
        self.remaining_when_paused = None
        self.timer_state = 'idle'
        self._battery_tick = 0
        self._stats_tick = 0  # 每300tick(5分钟)保存历史统计
        self._state_save_tick = 0  # 每30tick(30秒)保存运行状态


        # 视频相关
        self.video_list = []
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

        # 电脑使用时长监控（每 3 小时提醒一次）
        self.computer_usage_hours_today = 0
        self.computer_usage_ticks = 0  # 每秒+1，/3600=hours
        self.last_computer_usage_check = datetime.now()
        self.computer_usage_reminder_given_at = None  # 记录上次提醒的周期数
        self.computer_3h_cycles_today = 0  # 今天已完成的 3 小时周期数
        self._computer_usage_save_tick = 0  # 每 60 tick 保存一次
        self._load_computer_usage()

        # 5分钟倒计时浮层状态
        self._study_countdown_active = False
        self._computer_countdown_active = False

        # 活动检测（密度感知）
        self._idle_auto_paused = False
        self._activity_interval = 60  # 当前有效间隔（分钟）
        self._idle_seconds_cached = _get_idle_seconds()  # 当前系统空闲秒数
        self._idle_check_tick = 0

        # 目标锚点
        self.goal_text = _load_goal() or ''

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
        # 创建20-20-20护眼提醒浮层
        self.eye_rest_overlay = EyeRestOverlay()
        # 启动时先定位到屏幕右侧，再显示（避免左上角闪烁）
        self.position_to_right()
        self.show()
        # 恢复上次运行状态（跨重启续接）
        self._restore_active_state()
        # 启动时提示设目标
        self._prompt_goal()

    def init_ui(self):
        self.setWindowTitle('休息提醒')
        self.widget_width = 380
        self.widget_height = 540
        self.setGeometry(100, 100, self.widget_width, self.widget_height)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
        self.app_icon = QIcon(ico_path)
        self.setWindowIcon(self.app_icon)
        self.setObjectName('mainWindow')

        # ── 全局样式 ──
        self.setStyleSheet("""
            QWidget {
                background-color: #08080c;
                border-radius: 20px;
                color: #e8e6e1;
            }
            QWidget#mainWindow {
                background: qradialgradient(cx:0.5, cy:0.0, radius:0.8,
                    stop:0 rgba(212, 175, 55, 0.05), stop:1 #08080c);
                border: 1px solid rgba(212, 175, 55, 0.10);
            }
            QLabel {
                color: #e8e6e1;
                font-size: 14px;
                background: transparent;
            }
            QPushButton {
                font-family: 'Georgia, "Noto Serif SC", serif';
                font-size: 11px;
                font-weight: 600;
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
            QPushButton#actionBtn {
                background-color: rgba(212, 175, 55, 0.10);
                color: #d4af37;
                border: 1px solid rgba(212, 175, 55, 0.25);
                border-radius: 20px;
                padding: 0 24px;
            }
            QPushButton#actionBtn:hover {
                background-color: rgba(212, 175, 55, 0.20);
                border-color: #d4af37;
            }
            QPushButton#actionBtn:disabled {
                background-color: transparent;
                color: #3a3835;
                border-color: #2a2928;
            }
            QPushButton#pauseBtn {
                background-color: rgba(255, 122, 80, 0.08);
                color: #ff7a50;
                border: 1px solid rgba(255, 122, 80, 0.20);
                border-radius: 20px;
                padding: 0 24px;
            }
            QPushButton#pauseBtn:hover {
                background-color: rgba(255, 122, 80, 0.16);
                border-color: #ff7a50;
            }
            QPushButton#pauseBtn:disabled {
                background-color: transparent;
                color: #3a3835;
                border-color: #2a2928;
            }
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: rgba(255,255,255,0.04);
                text-align: center;
                font-size: 10px;
                color: #666;
            }
            QProgressBar::chunk {
                border-radius: 3px;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(0)

        # ═══ 顶部：品牌 + 关闭 ═══
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.title_label = QLabel('⚡ 精力管理')
        self.title_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 12, QFont.Bold))
        self.title_label.setStyleSheet('color: #d4af37;')
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()

        # 目标锚点显示
        self.goal_label = QLabel('')
        self.goal_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.goal_label.setStyleSheet('color: #6a8cbb; background: transparent; padding: 3px 10px; border: 1px solid rgba(106, 140, 187, 0.15); border-radius: 20px;')
        self.goal_label.setAlignment(Qt.AlignCenter)
        self.goal_label.setMaximumWidth(160)
        if self.goal_text:
            self.goal_label.setText(f'{self.goal_text}')
        top_layout.addWidget(self.goal_label)
        top_layout.addStretch()

        self.close_btn = QPushButton('×')
        self.close_btn.setObjectName('closeBtn')
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip('隐藏窗口')
        self.close_btn.clicked.connect(self.hide)
        top_layout.addWidget(self.close_btn)
        main_layout.addLayout(top_layout)

        # ═══ 核心区域：大计时器 ═══
        main_layout.addSpacing(16)

        self.time_label = QLabel('续航 60:00')
        self.time_label.setFont(QFont('Consolas, "SF Mono", monospace', 56, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet('color: #d4af37; letter-spacing: 4px;')
        main_layout.addWidget(self.time_label)

        time_hint = QLabel('续航剩余')
        time_hint.setFont(QFont('Georgia, "Noto Serif SC", serif', 10))
        time_hint.setAlignment(Qt.AlignCenter)
        time_hint.setStyleSheet('color: #666; padding-bottom: 4px;')
        main_layout.addWidget(time_hint)

        # 主进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("""
            QProgressBar { background-color: #1a1918; }
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b6914, stop:0.5 #d4af37, stop:1 #f0d060); }
        """)
        main_layout.addWidget(self.progress_bar)

        # ═══ 按钮区 ═══
        main_layout.addSpacing(20)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.start_btn = QPushButton('▶ 开始')
        self.start_btn.setFont(QFont('Georgia, "Noto Serif SC", serif', 11, QFont.Bold))
        self.start_btn.setFixedHeight(40)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setObjectName('actionBtn')
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton('⏸ 暂停')
        self.pause_btn.setFont(QFont('Georgia, "Noto Serif SC", serif', 11, QFont.Bold))
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setObjectName('pauseBtn')
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        btn_layout.addWidget(self.pause_btn)
        main_layout.addLayout(btn_layout)

        # ═══ 分隔线 ═══
        main_layout.addSpacing(20)

        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.15 rgba(212,175,55,0.10), stop:0.85 rgba(212,175,55,0.10), stop:1 transparent);')
        main_layout.addWidget(sep)

        # ═══ 卡片区：2×2 统计网格 ═══
        main_layout.addSpacing(12)

        grid = QHBoxLayout()
        grid.setSpacing(8)

        # 左列
        left_col = QVBoxLayout()
        left_col.setSpacing(8)

        # 卡1: 今日产出
        card1 = QFrame()
        card1.setObjectName('statCard')
        card1.setStyleSheet("QFrame#statCard { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }")
        card1_layout = QVBoxLayout(card1)
        card1_layout.setContentsMargins(10, 10, 10, 10)
        card1_layout.setSpacing(4)

        card1_label = QLabel('今日产出')
        card1_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        card1_label.setStyleSheet('color: #666; letter-spacing: 1px; background: transparent; border: none;')
        card1_layout.addWidget(card1_label)

        self.study_progress_label = QLabel('📚 0h')
        self.study_progress_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 18, QFont.Bold))
        self.study_progress_label.setStyleSheet('color: #d4af37; background: transparent; border: none;')
        card1_layout.addWidget(self.study_progress_label)

        self.study_sub_label = QLabel('')
        self.study_sub_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.study_sub_label.setStyleSheet('color: #6a8cbb; background: transparent; border: none;')
        card1_layout.addWidget(self.study_sub_label)

        self.study_progress_bar = QProgressBar()
        self.study_progress_bar.setObjectName('study_bar')
        self.study_progress_bar.setMaximum(14)
        self.study_progress_bar.setValue(0)
        self.study_progress_bar.setTextVisible(False)
        self.study_progress_bar.setFixedHeight(2)
        self.study_progress_bar.setStyleSheet("QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b6914, stop:0.5 #d4af37, stop:1 #f0d060); border-radius: 1px; }")
        card1_layout.addWidget(self.study_progress_bar)
        left_col.addWidget(card1)

        # 卡2: 22:00 倒计时
        card2 = QFrame()
        card2.setObjectName('statCard')
        card2.setStyleSheet("QFrame#statCard { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }")
        card2_layout = QVBoxLayout(card2)
        card2_layout.setContentsMargins(10, 10, 10, 10)
        card2_layout.setSpacing(4)

        card2_label = QLabel('今日截止')
        card2_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        card2_label.setStyleSheet('color: #666; letter-spacing: 1px; background: transparent; border: none;')
        card2_layout.addWidget(card2_label)

        self.countdown_label = QLabel('⏳ 8h 37m')
        self.countdown_label.setFont(QFont('Consolas, "SF Mono", monospace', 18, QFont.Bold))
        self.countdown_label.setStyleSheet('color: #6a9bcc; background: transparent; border: none;')
        card2_layout.addWidget(self.countdown_label)

        self.countdown_bar = QProgressBar()
        self.countdown_bar.setObjectName('countdown_bar')
        self.countdown_bar.setMaximum(100)
        self.countdown_bar.setValue(100)
        self.countdown_bar.setTextVisible(False)
        self.countdown_bar.setFixedHeight(2)
        self.countdown_bar.setStyleSheet("QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a5a8a, stop:0.5 #6a9bcc, stop:1 #8ab8e0); border-radius: 1px; }")
        card2_layout.addWidget(self.countdown_bar)
        left_col.addWidget(card2)

        grid.addLayout(left_col)

        # 右列
        right_col = QVBoxLayout()
        right_col.setSpacing(8)

        # 卡3: 连续打卡
        card3 = QFrame()
        card3.setObjectName('statCard')
        card3.setStyleSheet("QFrame#statCard { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }")
        card3_layout = QVBoxLayout(card3)
        card3_layout.setContentsMargins(10, 10, 10, 10)
        card3_layout.setSpacing(4)

        card3_label = QLabel('连续打卡')
        card3_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        card3_label.setStyleSheet('color: #666; letter-spacing: 1px; background: transparent; border: none;')
        card3_layout.addWidget(card3_label)

        streak = self.streak_data
        self.streak_label = QLabel(f'{streak["current_streak"]}' if streak['current_streak'] > 0 else '0')
        self.streak_label.setFont(QFont('Consolas, "SF Mono", monospace', 24, QFont.Bold))
        self.streak_label.setStyleSheet('color: #d97757; background: transparent; border: none;')
        card3_layout.addWidget(self.streak_label)

        streak_sub = QLabel('天')
        streak_sub.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        streak_sub.setStyleSheet('color: #666; background: transparent; border: none;')
        card3_layout.addWidget(streak_sub)
        right_col.addWidget(card3)

        # 卡4: 今日休息
        card4 = QFrame()
        card4.setObjectName('statCard')
        card4.setStyleSheet("QFrame#statCard { background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); border-radius: 10px; padding: 10px 12px; }")
        card4_layout = QVBoxLayout(card4)
        card4_layout.setContentsMargins(10, 10, 10, 10)
        card4_layout.setSpacing(4)

        card4_label = QLabel('今日休息')
        card4_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        card4_label.setStyleSheet('color: #666; letter-spacing: 1px; background: transparent; border: none;')
        card4_layout.addWidget(card4_label)

        self.break_label = QLabel('☕ 0')
        self.break_label.setFont(QFont('Consolas, "SF Mono", monospace', 18, QFont.Bold))
        self.break_label.setStyleSheet('color: #6a9b6a; background: transparent; border: none;')
        card4_layout.addWidget(self.break_label)

        break_sub = QLabel('分钟')
        break_sub.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        break_sub.setStyleSheet('color: #666; background: transparent; border: none;')
        card4_layout.addWidget(break_sub)
        right_col.addWidget(card4)

        grid.addLayout(right_col)
        main_layout.addLayout(grid)

        # ═══ 底部：分隔 + 电脑使用 + 电池 ═══
        main_layout.addSpacing(12)

        sep2 = QLabel()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.15 rgba(212,175,55,0.06), stop:0.85 rgba(212,175,55,0.06), stop:1 transparent);')
        main_layout.addWidget(sep2)

        main_layout.addSpacing(10)

        row3 = QHBoxLayout()
        row3.setSpacing(8)

        self.computer_usage_label = QLabel('💻 0H00min')
        self.computer_usage_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.computer_usage_label.setStyleSheet('color: #7a5aab;')
        row3.addWidget(self.computer_usage_label)

        self.computer_usage_bar = QProgressBar()
        self.computer_usage_bar.setObjectName('computer_usage_bar')
        self.computer_usage_bar.setMaximum(100)
        self.computer_usage_bar.setValue(100)
        self.computer_usage_bar.setTextVisible(False)
        self.computer_usage_bar.setFixedHeight(2)
        self.computer_usage_bar.setStyleSheet("QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a2a7a, stop:0.5 #7a5aab, stop:1 #9b6acc); border-radius: 1px; }")
        row3.addWidget(self.computer_usage_bar)

        self.battery_label = QLabel('🔋 检测中')
        self.battery_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.battery_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.battery_label.setStyleSheet('color: #5a8a30;')
        row3.addWidget(self.battery_label)

        self.battery_bar = QProgressBar()
        self.battery_bar.setObjectName('battery_bar')
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(False)
        self.battery_bar.setFixedHeight(3)
        self.battery_bar.setStyleSheet("""
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3a5a20, stop:0.5 #5a8a30, stop:1 #788c57); }
        """)
        main_layout.addWidget(self.battery_bar)

        # ── 底部退出按钮 ──
        exit_row = QHBoxLayout()
        exit_row.setContentsMargins(0, 6, 0, 0)
        exit_row.addStretch()
        self.exit_btn = QPushButton('退出程序')
        self.exit_btn.setFixedHeight(22)
        self.exit_btn.setCursor(Qt.PointingHandCursor)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                color: #3a3835; background: transparent;
                border: none; font-size: 9px; padding: 2px 10px;
                font-family: 'Georgia, "Noto Serif SC", serif';
                letter-spacing: 0.5px;
            }
            QPushButton:hover {
                color: #d4af37;
                background: rgba(212, 175, 55, 0.06);
                border-radius: 4px;
            }
        """)
        self.exit_btn.clicked.connect(self.quit_app)
        exit_row.addWidget(self.exit_btn)
        main_layout.addLayout(exit_row)

        self.setLayout(main_layout)

        # ═══ 呼吸灯动画 ═══
        self._glow_opacity = 0
        self._glow_dir = 1
        self._glow_timer = QTimer()
        self._glow_timer.timeout.connect(self._update_glow)
        self._glow_timer.start(50)

    def _update_glow(self):
        """呼吸灯：运行时计时器颜色脉动"""
        if not self.timer.isActive():
            self._glow_opacity = 0
            self.time_label.setStyleSheet('color: #d4af37; letter-spacing: 4px;')
            return
        self._glow_opacity += self._glow_dir * 2
        if self._glow_opacity >= 30:
            self._glow_dir = -1
        elif self._glow_opacity <= 0:
            self._glow_dir = 1
        o = self._glow_opacity
        r = 180 + o * 2
        g = 140 + o
        self.time_label.setStyleSheet(
            f'color: rgb({r},{g},30); letter-spacing: 4px;')

    def show_stats(self):
        """显示学习统计窗口"""
        LocalSync.save_daily_stats()
        if not hasattr(self, '_stats_window') or self._stats_window is None:
            self._stats_window = StatsWindow()
        self._stats_window.show()
        self._stats_window.raise_()

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
        script = os.path.abspath(os.path.join(os.path.dirname(__file__), 'watchdog.py'))
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
            pass
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
        self.tray_icon.setToolTip('⚡ 精力管理 · 待开始')
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 自定义托盘卡片
        self.tray_card = TrayCardWidget()
        self.tray_card.action_requested.connect(self.on_tray_card_action)

        # 仍然保留原生 QMenu 作为兜底（某些 Windows 版本右键行为不一致）
        self._init_fallback_menu()

        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.show()

    def _init_fallback_menu(self):
        """原生 QMenu 兜底"""
        tray_menu = QMenu()
        toggle_action = QAction('显示/隐藏', self)
        toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(toggle_action)
        tray_menu.addSeparator()
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
        elif reason == QSystemTrayIcon.Context:
            # 右键 → 弹出自定义卡片
            self._show_tray_card()

    def _show_tray_card(self):
        """在托盘图标旁边弹出自定义卡片"""
        # 更新数据
        streak = self.streak_data.get('current_streak', 0)
        self.tray_card.update_data(
            study_hours=int(self.study_hours_today),
            streak=streak,
            break_minutes=int(self.break_minutes_today),
            autostart=self.is_autostart_enabled(),
            reminder_mode=self.app_settings.get('reminder_mode', 'video'),
        )
        # 定位到托盘图标附近
        cursor_pos = QCursor.pos()
        self.tray_card.show_at(cursor_pos)

    def on_tray_card_action(self, action):
        """处理托盘卡片的操作信号"""
        if action == 'toggle_visibility':
            self.toggle_visibility()
            self.tray_card.close()
        elif action == 'toggle_autostart':
            self.toggle_autostart()
            self.tray_card.update_data(autostart=self.is_autostart_enabled())
        elif action == 'show_stats':
            self.show_stats()
            self.tray_card.close()
        elif action == 'export_data':
            self.export_weekly_data()
            self.tray_card.close()
        elif action == 'quit_app':
            self.quit_app()
        elif action == 'toggle_pin':
            self.tray_card.close()
        elif action.startswith('set_mode:'):
            mode = action.split(':', 1)[1]
            self._set_reminder_mode(mode)
            self.tray_card.update_data(reminder_mode=mode)

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

    def _pause_timer(self, auto_paused=False):
        """暂停计时器（计算剩余时间）"""
        remaining = self._activity_interval * 60 - (datetime.now() - self.start_time).total_seconds()
        self.remaining_when_paused = max(remaining, 0)
        self.timer_state = 'paused'
        if not auto_paused:
            self._idle_auto_paused = False
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
        self._idle_seconds_cached = 0
        self._sync_buttons()

    def on_start_clicked(self):
        try:
            if self.timer_state not in ('idle', 'paused'):
                return
            if self.timer_state == 'idle':
                # 休息时长追踪：如果有 break_start，计算休息时长
                if self.break_start is not None:
                    break_duration = (datetime.now() - self.break_start).total_seconds()
                    break_mins = round(break_duration / 60, 1)
                    self.break_minutes_today += break_mins
                    LocalSync.save_break_minutes(self.break_minutes_today)
                    log.info(f'[休息追踪] 本次休息 {break_mins:.1f} 分钟，今日累计 {self.break_minutes_today:.1f} 分钟')
                    self.break_start = None
                    self._update_break_display()
                self.start_time = datetime.now()
                self._idle_auto_paused = False
                self._idle_seconds_cached = 0
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
            # 学习倒计时结束，但电脑使用倒计时可能还在运行
            if not self._computer_countdown_active:
                self.countdown_overlay.hide_overlay()
            self._sync_buttons()
        except Exception as e:
            log.error(f'[_reset_timer_to_idle 异常] {type(e).__name__}: {e}')

    def _handle_idle(self):
        """处理空闲状态 - 显示默认时间或休息中"""
        if self.break_start is not None:
            # 休息中，实时显示休息时长
            elapsed_mins = (datetime.now() - self.break_start).total_seconds() / 60
            self.time_label.setText(f'☕ 休息中 {int(elapsed_mins)}m')
            self.progress_bar.setValue(0)
            self._update_break_display()
            self.tray_icon.setToolTip(f'⚡ 精力管理 · ☕ 休息中 {int(elapsed_mins)}m')
        else:
            self.time_label.setText(f'续航 {self._activity_interval:02d}:00')
            self.progress_bar.setValue(0)
            self.tray_icon.setToolTip(f'⚡ 精力管理 · 续航 {self._activity_interval}min')

    def _handle_running(self, now):
        """处理运行状态 - 倒计时 + 活动密度感知"""
        elapsed = (now - self.start_time).total_seconds()
        # 动态间隔：高密度→45min，普通→60min
        self._idle_check_tick += 1
        if self._idle_check_tick >= 15:
            self._idle_check_tick = 0
            idle = _get_idle_seconds()
            # idle > 上次值 → 无新输入，用户在空闲
            # idle < 上次值 → idle计时器重置了，用户有输入
            if idle > self._idle_seconds_cached:  # 空闲持续增长
                consecutive_idle = idle
                if consecutive_idle > 300 and not self._idle_auto_paused:
                    self._idle_auto_paused = True
                    self._pause_timer(auto_paused=True)
                    self.tray_icon.showMessage('⏸ 检测到空闲', '已自动暂停（连续5分钟无操作）', QSystemTrayIcon.Information, 2000)
                    log.info(f'[活动检测] 连续空闲{idle}s, 自动暂停')
                elif consecutive_idle < 30 and elapsed > 600:
                    self._activity_interval = 60  # 空闲中保持60min
                else:
                    self._activity_interval = 60
            else:  # idle 重置了 → 用户有操作，缩间隔
                if elapsed > 600:
                    self._activity_interval = 45  # 活跃用户缩到45min高密度模式
            self._idle_seconds_cached = idle

        total_seconds = self._activity_interval * 60
        remaining = max(total_seconds - elapsed, 0)

        # 更新显示
        mins = int(remaining // 60)
        secs = int(remaining % 60)
        # 加上活动指标
        busy_indicator = '🔥' if self._activity_interval < 60 else '⚡'
        self.time_label.setText(f'{busy_indicator} {mins:02d}:{secs:02d}')
        # 托盘提示
        self.tray_icon.setToolTip(f'⚡ 精力管理 · 剩余 {mins}:{secs:02d}')

        # 更新进度条
        progress = int((elapsed / total_seconds) * 100)
        self.progress_bar.setValue(min(progress, 100))

        # 最后5分钟倒计时浮层 - 只在进入阈值时启动，不重复调
        if remaining <= 300 and remaining > 0 and not self._study_countdown_active:
            self._study_countdown_active = True
            self.countdown_overlay.show_countdown(
                remaining,
                '📚 学习即将结束',
                random.choice([
                    '还剩不到5分钟，准备休息一下~',
                    '快到休息时间了，站起来活动活动~',
                    '还有一小会儿，准备喝口水~',
                    '即将休息，眼睛可以放松一下了~',
                    '最后一小段，撑住！（请辨：耐心本身就是门槛）',
                ]),
                total_seconds=300
            )
        # 还在阈值外 → 清理浮层状态
        if remaining > 300 and self._study_countdown_active:
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()
        # 倒计时结束
        if remaining <= 0:
            self._study_countdown_active = False
            self._activity_interval = 60
            self._reset_eye_rest()
            # 不直接隐藏浮层：电脑使用倒计时可能还在运行
            if not self._computer_countdown_active:
                self.countdown_overlay.hide_overlay()
            # 记录休息开始时间（用于追踪休息时长）
            self.break_start = datetime.now()
            self._rest_break_tick = 0      # 重置休息5分钟计数
            log.info(f'[休息追踪] 倒计时结束，break_start={self.break_start.strftime("%H:%M:%S")}')
            # 根据提醒方式设置决定动作
            reminder_mode = self.app_settings.get('reminder_mode', 'video')
            if reminder_mode == 'video':
                self.open_random_video()
            elif reminder_mode == 'notify':
                self.tray_icon.showMessage(
                    '休息时间到！',
                    '倒计时结束，记得放松一下哦~',
                    QSystemTrayIcon.Information,
                    3000
                )
            elif reminder_mode == 'quote':
                quote, tag = _pick_quote()
                self.tray_icon.showMessage(
                    '💡 请辨 · 休息思辨',
                    f'{quote}\n——{tag}',
                    QSystemTrayIcon.Information,
                    6000
                )
            else:  # 'none'
                log.info('[提醒方式] 无操作模式，不弹通知不打开视频')
            self.study_hours_today += 1
            self.update_study_display()
            LocalSync.increment_study_hour(self.study_hours_today)

            # 快速复盘弹窗：休息前问"这小时产出自评"
            self._pending_review = True
            self._prompt_review()

            self._reset_timer_to_idle()

    def _handle_paused(self, now):
        """处理暂停状态 - 显示暂停时间"""
        if self._idle_auto_paused:
            self.time_label.setText('⏸ 空闲暂停')
            self.tray_icon.setToolTip('⚡ 精力管理 · ⏸ 空闲暂停')
        elif self.remaining_when_paused is None:
            self.time_label.setText('⏸ 已暂停')
            self.tray_icon.setToolTip('⚡ 精力管理 · ⏸ 已暂停')
            return
        else:
            mins = int(self.remaining_when_paused // 60)
            secs = int(self.remaining_when_paused % 60)
            self.time_label.setText(f'⏸ 已暂停：{mins:02d}:{secs:02d}')
            self.tray_icon.setToolTip(f'⚡ 精力管理 · ⏸ 剩余 {mins}:{secs:02d}')
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
            computer = self.computer_usage_hours_today
            computer_h = int(computer)
            computer_m = int((computer - computer_h) * 60)
            msg = (f'今日学习：{study} 小时\n'
                   f'今日电脑使用：{computer_h} 小时 {computer_m} 分钟\n\n'
                   f'记得记录到飞书～')
            self.tray_icon.showMessage('📋 每日记录提醒', msg, QSystemTrayIcon.Information, 8000)
            log.info(f'[DailyReport] 22:00 提醒: 学习{study}h, 电脑{computer:.1f}h')
            # 检查连续打卡
            self._check_streak()

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
                self.computer_usage_hours_today = 0
                self.computer_usage_ticks = 0
                self.computer_3h_cycles_today = 0
                self.computer_usage_reminder_given_at = None
                self._activity_interval = 60  # 新的一天重置为60min
                self._idle_auto_paused = False
                self._study_countdown_active = False
                self._computer_countdown_active = False
                self._reset_eye_rest()
                self.countdown_overlay.hide_overlay()
                self.current_date = now.date()
                self._daily_report_shown_today = False
                LocalSync.reset()
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

            # --- 20-20-20 护眼提醒（仅在学习计时器运行时） ---
            if self.timer_state == 'running':
                self.eye_rest_elapsed += 1
                if self.eye_rest_elapsed >= self.eye_rest_interval:
                    self.eye_rest_elapsed = 0
                    self._show_eye_rest_reminder()
            elif self.timer_state == 'idle' and self.break_start is not None:
                # 休息期间重置计数，下次学习重新开始 20 分钟
                self._reset_eye_rest()

            # --- 休息5分钟提示音提醒 ---
            if self.timer_state == 'idle' and self.break_start is not None:
                self._rest_break_tick += 1
                if self._rest_break_tick % 300 == 0:  # 每5分钟
                    elapsed_rest_mins = int(self._rest_break_tick // 60)
                    self._play_rest_chime()
                    self.tray_icon.showMessage(
                        '☕ 休息提醒',
                        f'已休息 {elapsed_rest_mins} 分钟，该回去学习啦~',
                        QSystemTrayIcon.Information,
                        3000
                    )

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

            # --- 电脑使用时长累加与提醒 ---
            self.update_computer_usage(now)

        except Exception as e:
            log.error(f'[update_display 异常] {type(e).__name__}: {e}')
            traceback.print_exc()

    def update_study_display(self):
        """更新学习时长显示（卡片布局）"""
        h = self.study_hours_today
        self.study_progress_label.setText(f'{h}h')
        self.study_sub_label.setText(f'🎯 {self.goal_text}' if self.goal_text else '')
        self.study_progress_bar.setValue(h)

    def _update_break_display(self):
        """更新休息时长显示（卡片: 大号数字）"""
        if self.break_start is not None:
            elapsed = (datetime.now() - self.break_start).total_seconds() / 60
            self.break_label.setText(f'☕ {elapsed:.0f}')
        elif self.break_minutes_today > 0:
            self.break_label.setText(f'☕ {self.break_minutes_today:.0f}')
        else:
            self.break_label.setText('☕ 0')

    def _prompt_review(self):
        """快速复盘弹窗：这小时产出自评（QInputDialog）"""
        try:
            if not self._pending_review:
                return
            from PyQt5.QtWidgets import QInputDialog
            scores = ['1⭐ 摸鱼', '2⭐ 一般', '3⭐ 还行', '4⭐ 不错', '5⭐ 专注']
            score_str, ok = QInputDialog.getItem(
                self, '快速复盘', '这小时产出怎么样？', scores, 0, False
            )
            if ok and score_str:
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
        try:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.review_log.json')
            data = {}
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            today = datetime.now().date().isoformat()
            if today not in data:
                data[today] = []
            data[today].append({
                'time': datetime.now().strftime('%H:%M'),
                'score': score
            })
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.error(f'[复盘] 保存失败: {e}')

    def _prompt_goal(self):
        """启动时弹出目标选择"""
        if self.goal_text:
            return
        try:
            self.goal_label.setText('🎯 点我设今日目标')
            self.goal_label.setStyleSheet('color: #6a9bcc; cursor: pointer; background: transparent;')
            self.goal_label.mousePressEvent = self._show_goal_dialog
        except Exception as e:
            log.error(f'[目标] 提示异常: {e}')

    def _show_goal_dialog(self, event=None):
        """显示目标选择对话框（event 参数用于 mousePressEvent 回调）"""
        try:
            goals = _GOAL_OPTIONS
            goal, ok = QInputDialog.getItem(self, '设定今日目标', '今天主要做什么？', goals, 0, False)
            if ok and goal:
                self.goal_text = goal
                _save_goal(goal)
                self.goal_label.setText(f'🎯 {goal}')
                self.goal_label.setStyleSheet('color: #7a9bcc; background: transparent;')
                self.update_study_display()
                log.info(f'[目标] 设定为: {goal}')
        except Exception as e:
            log.error(f'[目标] 对话框异常: {e}')

    def _show_eye_rest_reminder(self):
        """显示 20-20-20 护眼提醒浮窗"""
        self.eye_rest_overlay.show_reminder()
        log.info('[EyeRest] 20-20-20 护眼提醒触发')

    def _reset_eye_rest(self):
        """重置护眼计时器（每次学习周期结束/日期切换时调用）"""
        self.eye_rest_elapsed = 0
        self.eye_rest_overlay.hide_overlay()

    def _set_reminder_mode(self, mode):
        """设置提醒方式"""
        self.app_settings['reminder_mode'] = mode
        LocalSync.save_settings(self.app_settings)
        # 更新菜单勾选状态
        for key, action in self._reminder_actions.items():
            action.setChecked(key == mode)
        mode_names = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '只弹通知', 'none': '无操作'}
        self.tray_icon.showMessage('提醒方式', f'已切换为：{mode_names.get(mode, mode)}', QSystemTrayIcon.Information, 2000)
        log.info(f'[设置] 提醒方式切换为: {mode}')

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
        self.eye_rest_elapsed = state.get('eye_rest_elapsed', 0)
        # 恢复活动感知间隔
        saved_interval = state.get('activity_interval')
        if saved_interval and saved_interval in (45, 60):
            self._activity_interval = saved_interval
        self.update_study_display()
        self._update_break_display()

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
            'eye_rest_elapsed': self.eye_rest_elapsed,
            'activity_interval': self._activity_interval,
        }
        LocalSync.save_app_state(state)

    def _check_streak(self):
        """检查连续打卡：学习时长>=4小时则打卡，带里程碑金句"""
        today = datetime.now().date().isoformat()
        streak = self.streak_data
        if self.study_hours_today >= 4:
            if streak.get('last_streak_date') != today:
                streak['current_streak'] = streak.get('current_streak', 0) + 1
                streak['last_streak_date'] = today
                if streak['current_streak'] > streak.get('best_streak', 0):
                    streak['best_streak'] = streak['current_streak']
                log.info(f'[打卡] 今日学习{self.study_hours_today}h >= 4h，连续打卡 {streak["current_streak"]} 天')
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
        else:
            if streak.get('last_streak_date') != today:
                streak['current_streak'] = 0
                log.info(f'[打卡] 今日学习{self.study_hours_today}h < 4h，打卡中断')
        self.streak_data = streak
        LocalSync.save_streak(streak)
        self._update_streak_display()

    def _update_streak_display(self):
        """更新连续打卡显示（仅显示数字，大字）"""
        streak = self.streak_data
        if streak['current_streak'] > 0:
            self.streak_label.setText(f'{streak["current_streak"]}' )
        else:
            self.streak_label.setText('🔥 连续打卡：0天')

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
                self.computer_usage_ticks = int(data.get('hours', 0) * 3600)
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
        """更新电脑使用时长（倒计时模式：3 小时→0），tick计数避免浮点误差"""
        # 每秒+1 tick，累计/3600 = 小时
        self.computer_usage_ticks += 1
        self.computer_usage_hours_today = self.computer_usage_ticks / 3600.0

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

        # 最后5分钟倒计时浮层 - 只在进入阈值时启动，不重复调
        remaining_seconds = remaining_min * 3600
        if remaining_seconds <= 300 and remaining_seconds > 0 and not self._computer_countdown_active:
            self._computer_countdown_active = True
            self.countdown_overlay.show_countdown(
                remaining_seconds,
                '💻 电脑使用即将到期',
                random.choice([
                    '还剩不到5分钟，准备休息眼睛~',
                    '用电脑太久啦，待会儿远眺一下~',
                    '马上到时间了，起来走走吧~',
                    '快到休息时间，让眼睛放个假~',
                ]),
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
            LocalSync.increment_computer_hour(self.computer_usage_hours_today)
            self._save_computer_usage()
            log.info(f'[ComputerUsage] 触发第 {current_cycle} 个 3 小时周期')
        else:
            # 每 120 秒（2分钟）保存一次计数（防止重启丢失），用 tick 计数器避免浮点精度问题
            self._computer_usage_save_tick += 1
            if self._computer_usage_save_tick >= 120:
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
        """获取 B 站收藏夹视频列表（带重试，DNS 错误只记一次）"""
        import re as _re  # 模块级 re 在 daemon 线程中偶尔不可用，本地导入兜底
        fid = '3648313921'
        mid = '529362421'

        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
        ]

        self._bilibili_dns_error_logged = False  # DNS 错误只记一次，避免刷屏

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
                        if bvid and _re.match(r'^BV[a-zA-Z0-9]{10}$', bvid):
                            videos.append(f'https://www.bilibili.com/video/{bvid}')

                    if len(medias) < page_size:
                        break
                    page += 1

                if videos:
                    log.info(f'获取到 {len(videos)} 个收藏视频（{page} 页，第{attempt+1}次尝试）')
                    return videos

            except Exception as e:
                # DNS 错误只记一次，避免 WARP 下每次轮询都刷屏
                if not self._bilibili_dns_error_logged:
                    log.error(f'获取视频列表异常 (尝试 {attempt+1}/3): {e}')
                    self._bilibili_dns_error_logged = True
                elif 'getaddrinfo failed' not in str(e):
                    log.error(f'获取视频列表异常 (尝试 {attempt+1}/3): {e}')

            if attempt < 2:
                time.sleep(2)

        # 兜底方案
        if not self._bilibili_dns_error_logged:
            log.info('API 3 次全部失败，尝试从收藏夹页面提取视频链接...')
        try:
            page_url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create'
            resp = requests.get(page_url, headers={'User-Agent': user_agents[0], 'Referer': 'https://www.bilibili.com'}, timeout=10)
            bvids = _re.findall(r'BV[a-zA-Z0-9]{10}', resp.text)
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
        """打开B站收藏夹页面"""
        try:
            fav_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create'
            open_url(fav_url)
            log.info(f'打开收藏夹：{fav_url}')
            self.tray_icon.showMessage(
                '休息时间到！',
                '已为您打开B站收藏夹，记得放松一下哦~',
                QSystemTrayIcon.Information,
                3000
            )
        except Exception as e:
            log.error(f'[open_random_video 异常] {type(e).__name__}: {e}')
            traceback.print_exc()

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
            self._save_active_state()
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
