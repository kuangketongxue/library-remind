"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
- 20-20-20 护眼提醒：每 20 分钟浮窗提示看远处 20 秒
- 监控电池充电状态
- 学习时长本地计数（每次倒计时完成算 1 小时）
- 数据本地持久化（.daily_log.json）
"""
import sys
import time
import random
import os
import json
import platform
import re
import requests
import ctypes
import msvcrt
import tempfile
from PyQt5 import sip
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox, QShortcut, QFrame, QTabWidget, QStackedWidget, QComboBox, QLineEdit, QScrollArea, QDialog, QSlider, QSpinBox, QGroupBox, QTextBrowser, QToolTip)
from PyQt5.QtCore import QTimer, Qt, QPoint, QEvent, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QIcon, QFont, QPainter, QColor, QBrush, QPen, QKeySequence
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from tray_card import TrayCardWidget
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
VERSION = 'v5.1.0'
AUTO_SUBMIT_SECONDS = 60  # 自动提交超时（秒），三处复用
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
settings_store  = JSONStore('.settings.json',       default={'reminder_mode': 'video', 'silent_start': False, 'close_to_tray': True, 'study_tracking': True, 'review_reminder': True, 'sound_enabled': True}, ensure_ascii=False)
streak_store    = JSONStore('.streak.json',         default={'current_streak': 0, 'last_streak_date': '', 'best_streak': 0}, ensure_ascii=False)
history_store   = JSONStore('.stats_history.json',  default={})
app_state_store = JSONStore('.app_state.json')
review_store    = JSONStore('.review_log.json',     default={},          ensure_ascii=False, indent=2)


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
    14:   ("习惯成自然", "两周——你已经超过90%的人"),
    30:   ("月度王者", "30天——坚持的力量"),
    60:   ("二月不败", "60天——你已经是别人的榜样"),
    90:   ("季度冠军", "90天——质的飞跃"),
    365:  ("年度传奇", "365天——你改变了自己"),
}

STREAK_THRESHOLD_HOURS = 4  # 每日学习满此小时数才算打卡

_SUBJECTS = ['语', '数', '英', '物', '化', '政', '其他']
_LABELS = ['专注', '疲劳', '收获大', '走神', '其他']

_SCORE_COLORS_OLD = {1: '#ff4444', 2: '#ff8844', 3: '#fcc419', 4: '#78B450', 5: '#51cf66'}


def _score_to_color(score):
    """评分条填充色：旧格式(1-5)离散色板，新格式(1-100)三元映射"""
    if score <= 5:
        return _SCORE_COLORS_OLD.get(score, '#555')
    return '#51cf66' if score >= 80 else '#fcc419' if score >= 60 else '#ff8844'


def _score_bar_width(score, is_old=False):
    """评分条宽度：旧格式 score/5×100→×3，新格式 score×3"""
    pct = score / 5 * 100 if is_old else score
    return min(max(int(pct * 3), 6), 300)


def _is_old_format(scores):
    """判断评分列表是否为旧格式（1-5），取前3条判定"""
    return any(s <= 5 for s in scores[:3])


def _review_summary(entries):
    """从复盘条目列表提取结构化摘要数据"""
    scores_v = [e.get('score', 0) for e in entries]
    is_old = _is_old_format(scores_v)
    avg = sum(scores_v) / len(scores_v) if scores_v else 0
    if scores_v:
        best_idx = max(range(len(scores_v)), key=lambda i: scores_v[i])
        worst_idx = min(range(len(scores_v)), key=lambda i: scores_v[i])
    else:
        best_idx = worst_idx = 0
    return {
        'is_old': is_old, 'avg': avg, 'count': len(entries),
        'best': entries[best_idx] if entries else None,
        'worst': entries[worst_idx] if entries else None,
        'scores': scores_v,
    }


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
    """浮球（⏰ 60×60）— 点击弹出 info 浮层，右键菜单"""
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

        # 内层圆
        painter.setBrush(QBrush(QColor(20, 20, 24)))
        painter.setPen(QPen(QColor(212, 175, 55, 80), 1.5))
        painter.drawEllipse(2, 2, 56, 56)

        # ⚡ 图标
        painter.setPen(QColor(212, 175, 55))
        painter.setFont(QFont('Arial', 22, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, '⚡')

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
            delta = (datetime.now() - self.click_time).total_seconds()
            if delta < 0.3:
                # 短点击 → 弹出 info 浮层
                self._show_info_popup()

    def _show_info_popup(self):
        """点击浮球弹出 info 浮层（距离休息/学习时长/电脑时长 + 开始/暂停按钮）"""
        mw = self.main_window

        # 如果已显示就隐藏，否则创建（首次）或显示
        if hasattr(mw, '_info_popup') and mw._info_popup.isVisible():
            mw._info_popup.hide()
            return

        popup = getattr(mw, '_info_popup', None)
        if popup is None:
            # ★ 首次创建：构建整个 widget 树
            popup = QWidget(None)
            popup.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
            popup.setAttribute(Qt.WA_TranslucentBackground)
            popup.setAttribute(Qt.WA_DeleteOnClose)
            popup.setFixedSize(200, 130)

            root = QFrame(popup)
            root.setGeometry(4, 4, 192, 122)
            root.setObjectName('infoRoot')
            root.setStyleSheet("""
                QFrame#infoRoot {
                    background-color: rgba(20, 20, 24, 235);
                    border: 1px solid rgba(212, 175, 55, 0.15);
                    border-radius: 12px;
                }
                QLabel { background: transparent; }
            """)

            layout = QVBoxLayout(root)
            layout.setContentsMargins(10, 8, 8, 8)
            layout.setSpacing(4)

            # ── 顶部行：标题 + 右上角关闭按钮 ──
            top_row = QHBoxLayout()
            top_row.setContentsMargins(0, 0, 0, 0)
            title_lbl = QLabel('精力管理')
            title_lbl.setFont(QFont('Microsoft YaHei', 9))
            title_lbl.setStyleSheet('color: #777;')
            top_row.addWidget(title_lbl)
            top_row.addStretch()

            close_btn = QPushButton('✕')
            close_btn.setFixedSize(22, 22)
            close_btn.setCursor(Qt.PointingHandCursor)
            close_btn.setToolTip('关闭')
            close_btn.setStyleSheet("""
                QPushButton {
                    background: transparent; border: none;
                    color: #555; font-size: 14px; font-weight: bold;
                    border-radius: 11px;
                }
                QPushButton:hover {
                    background: rgba(255,80,80,0.20); color: #ff6b6b;
                }
            """)
            close_btn.clicked.connect(popup.hide)
            top_row.addWidget(close_btn)
            layout.addLayout(top_row)

            # 计时器
            popup._timer_lbl = QLabel('')
            popup._timer_lbl.setFont(QFont('Consolas, "SF Mono", monospace', 14, QFont.Bold))
            popup._timer_lbl.setStyleSheet('color: #d4af37;')
            popup._timer_lbl.setAlignment(Qt.AlignCenter)
            layout.addWidget(popup._timer_lbl)

            row = QHBoxLayout()
            popup._study_lbl = QLabel('')
            popup._study_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._study_lbl.setStyleSheet('color: #78B450;')
            row.addWidget(popup._study_lbl)
            row.addStretch()
            layout.addLayout(row)

            # 目标 + 轮次
            goal_row = QHBoxLayout()
            goal_row.setContentsMargins(0, 0, 0, 0)
            goal_row.setSpacing(4)
            popup._goal_lbl = QLabel('')
            popup._goal_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._goal_lbl.setStyleSheet('color: #d4a853;')
            popup._goal_lbl.setAlignment(Qt.AlignLeft)
            goal_row.addWidget(popup._goal_lbl, 1)
            popup._round_lbl = QLabel('')
            popup._round_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._round_lbl.setStyleSheet('color: #888;')
            popup._round_lbl.setAlignment(Qt.AlignRight)
            goal_row.addWidget(popup._round_lbl, 0)
            layout.addLayout(goal_row)

            # 开始/暂停按钮（只连接一次）
            popup._action_btn = QPushButton()
            popup._action_btn.setFixedHeight(28)
            popup._action_btn.setCursor(Qt.PointingHandCursor)
            popup._action_btn.setStyleSheet('QPushButton { background: #3b82f6; color: #fff; border: none; border-radius: 6px; font-size: 11px; font-weight: bold; } QPushButton:hover { background: #2563eb; }')
            popup._action_btn.clicked.connect(self._on_popup_btn_clicked)
            layout.addWidget(popup._action_btn)

            mw._info_popup = popup

        # ★ 每次只更新文字，不重建 widget
        self._update_popup_text()

        # 定位到浮球左边
        ball_pos = self.frameGeometry().topLeft()
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            x = min(ball_pos.x() - 170, sg.width() - 200)
            y = min(ball_pos.y(), sg.height() - 110)
            y = max(y, 10)
        else:
            x = ball_pos.x() - 170
            y = ball_pos.y()
        popup.move(x, y)
        popup.show()
        popup.raise_()


    def _update_popup_text(self):
        """只更新 popup 的文字内容（不重建 widget，带文本缓存避免重复 setText）"""
        mw = self.main_window
        popup = getattr(mw, '_info_popup', None)
        if not popup or not hasattr(popup, '_timer_lbl'):
            return

        # 计算剩余时间
        try:
            if mw.timer_state == 'running':
                remaining = max(mw._activity_interval * 60 - (datetime.now() - mw.start_time).total_seconds(), 0)
                m, s = int(remaining // 60), int(remaining % 60)
                timer_text = f'⚡ {m:02d}:{s:02d}'
            elif mw.timer_state == 'resting':
                remaining = max(0, (mw._rest_end_time - datetime.now()).total_seconds())
                m, s = int(remaining // 60), int(remaining % 60)
                timer_text = f'☕ {m:02d}:{s:02d}'
            elif mw.timer_state == 'paused':
                r = mw.remaining_when_paused or 0
                m, s = int(r // 60), int(r % 60)
                timer_text = f'⏸ {m:02d}:{s:02d}'
            elif mw.break_start is not None:
                elapsed = int((datetime.now() - mw.break_start).total_seconds() / 60)
                timer_text = f'☕ {elapsed}m'
            else:
                timer_text = f'续航 {mw._activity_interval:02d}:00'

            study = f'📚 {mw.study_hours_today:.1f}h'
        except Exception as e:
            timer_text = '续航 60:00'
            study = '📚 0h'
            log.debug(f'[_update_popup_text] 计算异常: {e}')

        # 文本缓存：跳过无变化的 setText 避免 repaint storm
        prev = getattr(popup, '_prev_texts', {})
        if prev.get('timer') != timer_text:
            popup._timer_lbl.setText(timer_text)
            prev['timer'] = timer_text
        if prev.get('study') != study:
            popup._study_lbl.setText(study)
            prev['study'] = study
        if hasattr(popup, '_goal_lbl'):
            goal = mw.goal_text or '🎯 未设目标'
            if prev.get('goal') != goal:
                popup._goal_lbl.setText(goal)
                popup._goal_lbl.setToolTip(goal)
                prev['goal'] = goal
        if hasattr(popup, '_round_lbl'):
            round_text = f'第{mw._round_count + 1}轮'
            if prev.get('round') != round_text:
                popup._round_lbl.setText(round_text)
                prev['round'] = round_text
        popup._prev_texts = prev

        # 更新按钮文字
        btn_map = {'running': 'pause', 'idle': 'start', 'paused': 'start', 'resting': 'rest'}
        btn_text_map = {'running': '⏸ 暂停', 'idle': '▶ 开始学习', 'paused': '▶ 开始学习', 'resting': '休息中...'}
        key = btn_map.get(mw.timer_state, 'start')
        if prev.get('btn') != key:
            popup._action_btn.setText(btn_text_map.get(mw.timer_state, '▶ 开始学习'))
            prev['btn'] = key

    def _on_popup_btn_clicked(self):
        """popup 按钮点击：开始/暂停切换"""
        mw = self.main_window
        log.info(f'[popup-btn] clicked, state={mw.timer_state}, day_ended={mw._day_ended}')
        if mw.timer_state == 'running':
            mw.on_pause_clicked()
        elif mw.timer_state in ('idle', 'paused'):
            mw.on_start_clicked()
        # 状态已变，更新 popup 文字
        self._update_popup_text()

    def toggle_main_window(self):
        """显示/隐藏主窗口"""
        log.info(f'[toggle_main_window] visible={self.main_window.isVisible()}')
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

        # 隐藏挂件
        action_hide = menu.addAction("👁  隐藏挂件")
        action_hide.triggered.connect(self.hide)

        menu.addSeparator()

        # 退出
        action_quit = menu.addAction("✕  退出")
        action_quit.triggered.connect(self.quit_app)

        menu.exec_(pos)

    def open_main_window(self):
        """打开主窗口"""
        log.info(f'[open_main_window] visible={self.main_window.isVisible()}, minimized={self.main_window.isMinimized()}')
        self.main_window.show()
        self.main_window.activateWindow()
        self.main_window.raise_()

    def open_website(self):
        """打开官方网站"""
        open_url("https://crazy-rest-reminder.pages.dev")

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
        cls._data = {'date': today, 'study_hours': 0, 'break_minutes_today': 0}
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
        """文件锁降级方案：检查旧锁 → 清理 → 获取新锁"""
        if os.path.exists(self.lock_path):
            try:
                with open(self.lock_path, "r") as f:
                    old_pid = int(f.read().strip())
                if psutil.pid_exists(old_pid):
                    try:
                        proc = psutil.Process(old_pid)
                        if "rest_reminder" in " ".join(proc.cmdline()):
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass  # 进程已退出或不可访问，视为旧锁失效
            except (ValueError, IOError):
                pass
            # 旧锁已失效，直接删除
            try:
                os.remove(self.lock_path)
            except Exception as e:
                log.warning(f"[单实例] 删除旧锁文件失败: {e}")
        # 获取新锁（原子操作）
        lh = open(self.lock_path, "w")
        msvcrt.locking(lh.fileno(), msvcrt.LK_NBLCK, 1)
        lh.write(str(os.getpid()))
        lh.flush()
        self.lock_handle = lh
        self.lock_file = self.lock_path
        atexit.register(self.cleanup)
        return False
    def cleanup(self):
        try:
            if self.lock_handle:
                try:
                    msvcrt.locking(self.lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception as e:
                    log.warning(f'[单实例] 解锁失败: {e}')
                self.lock_handle.close()
                self.lock_handle = None
            if self.lock_file and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except Exception as e:
            log.warning(f'[单实例] 清理失败: {e}')


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
        except Exception as e:
            log.warning(f'[提醒音] 播放失败: {e}')

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
        self.setAttribute(Qt.WA_DeleteOnClose)
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
        self._bar_rects = []  # 存储柱子矩形区域用于 tooltip

        # 关闭按钮
        close_btn = QPushButton('✕', self)
        close_btn.setObjectName('closeBtn')
        close_btn.setFixedSize(28, 28)
        close_btn.move(388, 4)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.close)

        self.setMouseTracking(True)

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
            data = history.get(d, {})
            days.append({'label': label, 'study': data.get('study', 0)})

        # 找最大值
        vals = [d['study'] for d in days]
        max_val = max(max(vals, default=0), 1)

        # 画柱状图
        chart_top = 50
        chart_bottom = 260
        chart_height = chart_bottom - chart_top
        bar_width = 24
        gap = (380 - 7 * bar_width) / 8

        self._bar_rects = []
        for i, d in enumerate(days):
            x = int(30 + gap + i * (bar_width + gap))

            # 学习柱子（绿色）
            h = int((d['study'] / max_val) * chart_height)
            painter.setBrush(QBrush(QColor('#788C57')))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(x, chart_bottom - h, bar_width, h, 3, 3)
            self._bar_rects.append((QRect(x, chart_bottom - h, bar_width, h), d['label'], d['study'], '学习'))

            # 日期标签
            painter.setPen(QColor('#b0aea5'))
            painter.setFont(QFont('Microsoft YaHei', 8))
            painter.drawText(x + 2, chart_bottom + 15, d['label'])

            # 数值标签
            if d['study'] > 0:
                painter.setPen(QColor('#788C57'))
                painter.drawText(x + 2, chart_bottom - h - 5, f"{d['study']:.1f}")

        # 图例
        painter.setBrush(QBrush(QColor('#788C57')))
        painter.drawRect(30, 285, 12, 12)
        painter.setPen(QColor('#faf9f5'))
        painter.setFont(QFont('Microsoft YaHei', 9))
        painter.drawText(48, 296, '学习')

        # 总计
        total_study = sum(d['study'] for d in days)
        painter.setPen(QColor('#6a9bcc'))
        painter.setFont(QFont('Microsoft YaHei', 9))
        painter.drawText(100, 296, f'本周学习 {total_study:.1f}h')

    def mouseMoveEvent(self, event):
        # Tooltip 优先
        pos = event.pos()
        for rect, label, value, _ in self._bar_rects:
            if rect.contains(pos):
                QToolTip.showText(
                    self.mapToGlobal(event.pos()),
                    f'{label} {value:.1f}h',
                    self, rect, 2000
                )
                return
        # 拖拽
        if self._drag_pos is not None:
            self.move(event.globalPos() - self._drag_pos)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPos() - self.frameGeometry().topLeft()

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
        self.setFixedSize(560, 520)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self._refreshing = False  # 防并发刷新
        self._pending_tab = None   # 快速点击时保留最后一次目标
        self._pending_timer = None  # 防抖定时器
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
        # ★ 直接同步刷新，不用 QTimer（延迟导致竞态）
        self._refresh_active_tab()

    def _refresh_active_tab(self):
        """防抖刷新：快速点击时只处理最后一次，避免竞态丢数据"""
        # 停止之前的待处理刷新
        if self._pending_timer is not None:
            self._pending_timer.stop()
        # 记录当前 tab 作为目标
        self._pending_tab = self.tabs.currentIndex()
        # 150ms 防抖——快速点击全部合并为一次刷新
        self._pending_timer = QTimer(self)
        self._pending_timer.setSingleShot(True)
        self._pending_timer.timeout.connect(self._do_refresh)
        self._pending_timer.start(150)

    def _do_refresh(self):
        """实际执行刷新（由防抖定时器触发）"""
        self._pending_timer = None
        if getattr(self, '_refreshing', False):
            # 如果正在刷新，延迟再试一次
            QTimer.singleShot(50, self._do_refresh)
            return
        self._refreshing = True
        try:
            try:
                if sip.isdeleted(self):
                    return
            except (ImportError, RuntimeError):
                pass
            idx = self._pending_tab if self._pending_tab is not None else self.tabs.currentIndex()
            self._pending_tab = None
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
        except RuntimeError:
            pass  # WA_DeleteOnClose 后 C++ 对象已销毁，正常忽略
        except Exception as e:
            import traceback
            log.error(f'[TrendWindow] 刷新标签页失败: {type(e).__name__}: {e}')
            traceback.print_exc()
        finally:
            self._refreshing = False

    def _clear_tab(self, tab):
        """安全清除标签页内容"""
        old = tab.layout()
        if old:
            while old.count():
                item = old.takeAt(0)
                w = item.widget()
                if w is not None:
                    w.setParent(None)
                    w.deleteLater()
        # 新布局自动替换旧布局（Qt 处理）
        l = QVBoxLayout(tab)
        l.setContentsMargins(16, 12, 16, 12)
        l.setSpacing(6)
        return l

    # ── Tab 1: 今日复盘时间线 ──
    def _draw_review_timeline(self):
        # ★ 先加载数据，再清空布局（防止快速点击竞态丢数据）
        reviews_data = review_store.load()
        today = datetime.now().date().isoformat()
        entries = reviews_data.get(today, [])
        layout = self._clear_tab(self._review_tab)

        if not entries:
            layout.addWidget(QLabel('📭 今天还没有复盘记录'))
            layout.addStretch()
            return

        # 顶部摘要（兼容新旧格式）
        info = _review_summary(entries)
        sufx = '⭐' if info['is_old'] else '分'
        b = info['best']; w = info['worst']
        summary = QLabel(
            f'今日复盘 {info["count"]} 次 · 平均 {info["avg"]:.1f}{sufx}'
            f' · 最高 {b["time"]}({b["score"]}{sufx}) · 最低 {w["time"]}({w["score"]}{sufx})'
        )
        summary.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent; padding: 6px 0;')
        layout.addWidget(summary)

        # 时间线（每条记录一行，兼容新旧格式）
        for e in entries:
            row = QHBoxLayout()
            row.setSpacing(8)

            # 时间
            t = QLabel(e['time'])
            t.setStyleSheet('color: #6a8cbb; font-size: 11px; font-family: Consolas; background: transparent; min-width: 44px;')
            t.setFixedWidth(44)
            row.addWidget(t)

            # 评分条（自适应1-5或1-100）
            bar_bg = QWidget()
            bar_bg.setFixedHeight(22)
            bar_bg.setStyleSheet('background: #1a1a20; border-radius: 4px;')
            bar_l = QHBoxLayout(bar_bg)
            bar_l.setContentsMargins(2, 2, 2, 2)

            fill = QWidget()
            score = e['score']
            fill_color = _score_to_color(score)
            fill.setFixedWidth(_score_bar_width(score, is_old=False))
            fill.setFixedHeight(18)
            fill.setStyleSheet(f'background: {fill_color}; border-radius: 3px;')
            bar_l.addWidget(fill)
            bar_l.addStretch()
            row.addWidget(bar_bg, 1)

            # 学科+标签
            meta_parts = []
            if e.get('subject') and e['subject'] != '未记录':
                meta_parts.append(e['subject'])
            if e.get('label') and e['label'] != '未记录':
                meta_parts.append(e['label'])
            meta_text = ' | '.join(meta_parts) if meta_parts else (f'{score}分' if score > 5 else '⭐' * score)
            s = QLabel(meta_text)
            s.setStyleSheet(f'color: {fill_color}; font-size: 11px; background: transparent; min-width: 70px;')
            s.setFixedWidth(70)
            row.addWidget(s)

            layout.addLayout(row)

        layout.addStretch()

    # ── Tab 2: 周趋势 ──
    def _draw_weekly_trend(self):
        # ★ 先加载数据
        stats = history_store.load()
        today = datetime.now().date()
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            label = (today - timedelta(days=i)).strftime('%m/%d')
            data = stats.get(d, {})
            days.append({
                'label': label, 'study': data.get('study', 0)
            })

        layout = self._clear_tab(self._week_tab)
        if not layout:
            return
        t = QLabel('📅 近7天学习时长')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)
        self._draw_single_bar(layout, days)

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
            # 只聚合到今天的周
            if week_start > today:
                continue
            study = 0
            d = week_start
            while d <= week_end:
                k = d.isoformat()
                if k in stats:
                    study += stats[k].get('study', 0)
                d += timedelta(days=1)
            weeks.append({
                'label': f'{week_start.month}/{week_start.day}',
                'study': round(study, 1)
            })

        layout = self._clear_tab(self._month_tab)
        # 标题
        t = QLabel('📅 最近5周趋势（周聚合）')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)
        self._draw_single_bar(layout, weeks)

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
                    months[key] = {'study': 0, 'count': 0}
                months[key]['study'] += data.get('study', 0)
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
                'study': round(d['study'], 1)
            })

        layout = self._clear_tab(self._quarter_tab)
        t = QLabel('📈 近半年月度趋势')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        layout.addWidget(t)

        if len(month_data) >= 2:
            self._draw_single_bar(layout, month_data)
        else:
            layout.addWidget(QLabel('📭 数据不足，再积累几天就能看到趋势了'))
            layout.addStretch()

        # 总览统计（仅统计展示的最近6个月）
        total_study = sum(d['study'] for d in month_data)
        total_days = sum(months[m]['count'] for m in recent)
        avg_study = round(total_study / total_days, 1) if total_days else 0
        summary = QLabel(f'📊 统计周期内共 {total_days} 天 · 日均学习 {avg_study}h · 总学习 {total_study:.0f}h')
        summary.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent; padding: 6px 0;')
        layout.addWidget(summary)

    # ── Tab 5: 时段分析 ──
    def _draw_time_analysis(self):
        reviews = review_store.load()
        layout = self._clear_tab(self._time_tab)

        # 判断评分格式（新旧兼容）
        all_scores = [e['score'] for entries in reviews.values() for e in entries if isinstance(e, dict)]
        is_old = _is_old_format(all_scores) if all_scores else False

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
                    fill_style = _score_to_color(d['avg'])
                    fill.setFixedWidth(_score_bar_width(d['avg'], is_old=is_old))
                    fill.setFixedHeight(14)
                else:
                    fill.setFixedWidth(0)
                    fill_style = 'transparent'
                fill.setStyleSheet(f'background: {fill_style}; border-radius: 3px;')
                bar_l.addWidget(fill)
                bar_l.addStretch()
                row.addWidget(bar_bg, 1)

                if d['count'] > 0:
                    sufx = '⭐' if is_old else '分'
                    sl = QLabel(f'{d["avg"]}{sufx}')
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
        sufx = '⭐' if is_old else '分'
        info = QLabel(f'🏆 最佳时段: {best_h}:00-{best_h+1}:00 ({avg_scores[best_h]}{sufx}) · ⚠️ 待改进: {worst_h}:00-{worst_h+1}:00 ({avg_scores[worst_h]}{sufx})')
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
            fill_style = _score_to_color(avg)
            fill.setFixedWidth(_score_bar_width(avg, is_old=is_old))
            fill.setFixedHeight(16)
            fill.setStyleSheet(f'background: {fill_style}; border-radius: 3px;')
            bar_l.addWidget(fill)
            bar_l.addStretch()
            row.addWidget(bar_bg, 1)

            # 评分 + 次数
            sl = QLabel(f'{avg}分 ×{counts[h]}')
            sl.setStyleSheet(f'color: {fill_style}; font-size: 11px; background: transparent; min-width: 56px;')
            sl.setFixedWidth(56)
            row.addWidget(sl)

            layout.addLayout(row)

        layout.addSpacing(12)

        # ── 热力图：一周各时段学习强度 ──
        hm_data = [[0] * 24 for _ in range(7)]
        stats = history_store.load()
        for d_str, ddata in stats.items():
            try:
                dt = datetime.strptime(d_str, '%Y-%m-%d')
                dow = dt.weekday()  # 0=Mon
                hm_data[dow][dt.hour] += ddata.get('study', 0)
            except Exception:
                continue
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self._draw_heatmap(layout, hm_data, [f'{h}h' for h in range(24)], day_names, '一周学习热力图（时段×星期）')

        layout.addStretch()

    # ── 单柱状图绘制（学习时长 + 悬浮提示） ──
    def _draw_single_bar(self, layout, data):
        """在 layout 中绘制学习时长单柱图，鼠标悬浮显示数值"""
        chart = QWidget()
        chart.setFixedHeight(200)
        chart.setStyleSheet('background: transparent;')
        chart.setMouseTracking(True)

        def paint_chart(painter, chart_widget):
            painter.setRenderHint(QPainter.Antialiasing)
            n = len(data)
            if n == 0:
                return
            vals = [d['study'] for d in data]
            max_val = max(max(vals, default=0), 1)
            w = chart_widget.width()
            h = chart_widget.height()
            chart_top = 10
            chart_bottom = h - 36
            chart_height = chart_bottom - chart_top
            bar_w = min(28, int((w - 60) / (n + 1)))
            gap = int((w - 60 - n * bar_w) / (n + 1))

            chart_widget._bar_rects = []
            for i, d in enumerate(data):
                x = 30 + gap + i * (bar_w + gap)
                bar_h = int((d['study'] / max_val) * chart_height)

                # 柱子（绿色）
                painter.setBrush(QBrush(QColor('#788C57')))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(x, chart_bottom - bar_h, bar_w, bar_h, 3, 3)

                # 记录位置用于 tooltip
                chart_widget._bar_rects.append((QRect(x, chart_bottom - bar_h, bar_w, bar_h), d['label'], d['study']))

                # 日期
                painter.setPen(QColor('#888'))
                painter.setFont(QFont('Microsoft YaHei', 8))
                painter.drawText(x + bar_w // 2 - 8, chart_bottom + 14, d['label'])

                # 数值（非零时显示）
                if d['study'] > 0:
                    painter.setPen(QColor('#788C57'))
                    painter.drawText(x + bar_w // 2 - 8, chart_bottom - bar_h - 4, f"{d['study']:.1f}")

        chart.paintEvent = lambda e: paint_chart(QPainter(chart), chart)

        def on_mouse_move(e):
            pos = e.pos()
            for rect, label, value in chart._bar_rects:
                if rect.contains(pos):
                    QToolTip.showText(chart.mapToGlobal(e.pos()), f'{label} 学习 {value:.1f}h', chart, rect, 2000)
                    return
            QToolTip.hideText()

        chart.mouseMoveEvent = on_mouse_move
        layout.addWidget(chart)

    # ── 热力图绘制 ──
    def _draw_heatmap(self, layout, data, x_labels, y_labels, title='时段热力图'):
        """在 layout 中绘制热力图（7天 x 24小时）"""
        from math import floor
        card = QFrame()
        card.setObjectName('statCard')
        cl = QVBoxLayout(card)
        cl.setContentsMargins(16, 14, 16, 14)
        cl.setSpacing(8)

        t = QLabel(f'🔥 {title}')
        t.setStyleSheet('color: #b0aea5; font-size: 12px; background: transparent;')
        cl.addWidget(t)

        hm = QWidget()
        rows = len(y_labels)
        cols = len(x_labels)
        cell_size = 28
        hm.setFixedSize(cols * cell_size + 50, rows * cell_size + 10)
        hm.setStyleSheet('background: transparent;')

        def paint_hm(e):
            p = QPainter(hm)
            p.setRenderHint(QPainter.Antialiasing)
            # 找最大值用于归一化
            vals = [data[y][x] for y in range(rows) for x in range(cols)]
            mx = max(vals) if vals and max(vals) > 0 else 1

            for y in range(rows):
                for x in range(cols):
                    v = data[y][x]
                    intensity = v / mx
                    # 从深色到琥珀金
                    r = int(20 + intensity * 192)
                    g = int(20 + intensity * 147)
                    b = int(30 + intensity * 25)
                    p.setBrush(QBrush(QColor(f'rgb({r},{g},{b})')))
                    p.setPen(Qt.NoPen)
                    px = 50 + x * cell_size
                    py = y * cell_size
                    p.drawRoundedRect(px + 1, py + 1, cell_size - 2, cell_size - 2, 3, 3)
                    # 数值（仅非零）
                    if v > 0:
                        p.setPen(QColor('#fff' if intensity > 0.5 else '#888'))
                        p.setFont(QFont('Consolas', 7))
                        p.drawText(px + 6, py + 17, str(int(v)))

            # Y 轴标签（小时）
            for y, lbl in enumerate(y_labels):
                p.setPen(QColor('#666'))
                p.setFont(QFont('Consolas', 7))
                p.drawText(2, y * cell_size + 17, lbl)

        hm.paintEvent = paint_hm
        cl.addWidget(hm, 0, Qt.AlignLeft)
        layout.addWidget(card)

        # 总计
        total_study = sum(d['study'] for d in data)
        avg_study = round(total_study / len(data), 1)
        summary = QLabel(f'总计: 学习 {total_study:.1f}h  |  日均: 学习 {avg_study}h')
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


def _md_to_html(text):
    """轻量 markdown → HTML（带表格支持）"""
    lines = text.split('\n')
    out = []
    in_code = False
    table_buf = []
    in_table = False

    def _flush_table():
        nonlocal in_table
        if not table_buf:
            return
        rows_html = []
        for i, row in enumerate(table_buf):
            cells = [c.strip() for c in row.strip('|').split('|')]
            if i == 0:
                row_html = '<tr>' + ''.join(f'<th style="border:1px solid #252530;padding:6px 12px;color:#d4af37;font-weight:bold;">{c}</th>' for c in cells) + '</tr>'
            else:
                row_html = '<tr>' + ''.join(f'<td style="border:1px solid #252530;padding:6px 12px;color:#b8b4ac;">{c}</td>' for c in cells) + '</tr>'
            rows_html.append(row_html)
        out.append(f'<table style="border-collapse:collapse;width:100%;margin:8px 0;font-size:13px;">{"".join(rows_html)}</table>')
        table_buf.clear()
        in_table = False

    for line in lines:
        if line.strip().startswith('```'):
            _flush_table()
            if in_code:
                out.append('</pre>')
                in_code = False
            else:
                out.append('<pre style="background:#18181f;border:1px solid #252530;border-radius:8px;padding:10px;font-size:12px;font-family:Consolas,monospace;color:#e8e4dc;overflow-x:auto;">')
                in_code = True
            continue
        if in_code:
            out.append(line)
            continue
        if '|' in line and not line.strip().startswith('|--'):
            in_table = True
            table_buf.append(line)
            continue
        if in_table:
            _flush_table()
        if line.startswith('# '):
            out.append(f'<h1 style="color:#e8e6e1;font-size:18px;font-weight:bold;margin:16px 0 8px;">{line[2:]}</h1>')
        elif line.startswith('## '):
            out.append(f'<h2 style="color:#d4af37;font-size:15px;font-weight:bold;margin:12px 0 6px;">{line[3:]}</h2>')
        elif line.startswith('### '):
            out.append(f'<h3 style="color:#c4b8a0;font-size:13px;font-weight:bold;margin:10px 0 4px;">{line[4:]}</h3>')
        elif line.startswith('- '):
            out.append(f'<li style="margin-left:16px;color:#b8b4ac;line-height:1.8;">{line[2:]}</li>')
        elif line.strip().startswith('> '):
            out.append(f'<blockquote style="border-left:3px solid #d4af37;padding-left:10px;color:#888;margin:6px 0;">{line.strip()[2:]}</blockquote>')
        elif line.strip() == '---':
            out.append('<hr style="border:none;border-top:1px solid #252530;margin:12px 0;">')
        elif line.strip():
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#e8e6e1;">\1</strong>', line)
            line = re.sub(r'(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)', r'<em style="color:#c4b8a0;">\1</em>', line)
            if re.match(r'^\*\s', line):
                line = '•' + line[1:]
            out.append(f'<p style="color:#b8b4ac;line-height:1.7;margin:4px 0;">{line}</p>')
    _flush_table()
    if in_code:
        out.append('</pre>')
    return '\n'.join(out)


def _build_report_data(report_type):
    """根据报告类型从数据源提取摘要"""
    today = datetime.now().date()
    history = history_store.load() or {}
    reviews = review_store.load() or {}
    daily = daily_store.load() or {}

    # 筛选日期范围（days-1 因为包含当天）
    ranges = {
        'daily': 1, 'weekly': 7, 'monthly': 30,
        'quarterly': 90, 'yearly': 365
    }
    days = ranges.get(report_type, 7)
    start = today - timedelta(days=days - 1)  # daily→今天, weekly→近7天
    records = []
    for d, v in sorted(history.items()):
        try:
            if datetime.fromisoformat(d).date() >= start:
                records.append({'date': d, **v})
        except (ValueError, TypeError):
            pass

    # 汇总（history 存的是 study(小时)，需转分钟）
    total_study = sum(r.get('study', 0) for r in records) * 60  # hours → minutes
    # sessions: 日期范围内的复盘条目数（每条复盘 = 1 轮）
    sessions = 0
    # avg_quality: 日期范围内复盘条目的 score 平均值
    review_scores = []
    for d, items in sorted(reviews.items()):
        try:
            if datetime.fromisoformat(d).date() < start:
                continue
            entries = items if isinstance(items, list) else [items]
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                sessions += 1
                s = entry.get('score')
                if s:
                    review_scores.append(s)
        except (ValueError, TypeError):
            pass
    avg_quality = int(sum(review_scores) / len(review_scores)) if review_scores else 0

    review_records = []
    for d, items in sorted(reviews.items()):
        try:
            if datetime.fromisoformat(d).date() >= start:
                if isinstance(items, list):
                    review_records.extend(items)
                elif isinstance(items, dict):
                    review_records.append(items)
        except (ValueError, TypeError):
            pass

    tags = {}
    for r in review_records:
        for t in r.get('tags', []) if isinstance(r, dict) else []:
            tags[t] = tags.get(t, 0) + 1
    top_tags = sorted(tags.items(), key=lambda x: -x[1])[:5]

    return {
        'report_type': report_type,
        'date_range': f'{start} ~ {today}',
        'days': days,
        'total_study_hours': round(total_study / 60, 1),
        'sessions': sessions,
        'avg_quality': avg_quality,
        'top_tags': top_tags,
        'records': records[-10:],  # 最近10条
    }


def _call_ai(prompt, model='sensenova-6.7-flash-lite'):
    """调用 AI API（SenseNova 主 → Agnes 备），返回生成文本"""

    # 候选端点（按优先级）
    endpoints = [
        {'url': 'https://token.sensenova.cn/v1/chat/completions', 'key': None},
        {'url': 'https://apihub.agnes-ai.com/v1/chat/completions', 'key': None},
    ]

    headers_base = {'Content-Type': 'application/json'}
    body = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': '你是学习分析助手，根据用户的学习数据给出简洁有用的分析报告。用中文回答。'},
            {'role': 'user', 'content': prompt},
        ],
        'max_tokens': 800,
        'temperature': 0.7,
    }

    last_err = None
    for ep in endpoints:
        try:
            url = ep['url']
            # 尝试从 settings 读取对应 API key
            api_key = None
            if 'sensenova' in url:
                api_key = settings_store.get('sensenova_api_key') or os.environ.get('SENSENOVA_API_KEY')
            elif 'agnes' in url:
                api_key = settings_store.get('agnes_api_key') or os.environ.get('AGNES_API_KEY')

            if not api_key:
                last_err = f'未配置 API key（{url}）'
                continue

            headers = {**headers_base, 'Authorization': f'Bearer {api_key}'}
            resp = requests.post(url, json=body, headers=headers, timeout=30)

            if resp.status_code == 200:
                data = resp.json()
                content = data.get('choices', [{}])[0].get('message', {}).get('content', '')
                if content:
                    return {'ok': True, 'content': content, 'provider': url}
            else:
                last_err = f'HTTP {resp.status_code}: {resp.text[:200]}'
        except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
            last_err = str(e)

    return {'ok': False, 'error': f'所有 AI 服务不可用。最后错误：{last_err}'}


def generate_report(report_type, force_refresh=False):
    """生成 AI 学习分析报告（内联，不再依赖 pro_features）"""
    try:
        cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.report_cache')
        os.makedirs(cache_dir, exist_ok=True)

        cache_file = os.path.join(cache_dir, f'{report_type}.json')
        cache = {}
        if not force_refresh and os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as jf:
                    cache = json.load(jf)
                cached_time = cache.get('generated_at', '')
                # 缓存有效期：日报 4h / 周报 12h / 月报 24h / 季报 48h / 年报 72h
                ttl = {'daily': 4, 'weekly': 12, 'monthly': 24, 'quarterly': 48, 'yearly': 72}
                max_hours = ttl.get(report_type, 12)
                if cached_time:
                    gen = datetime.fromisoformat(cached_time)
                    if (datetime.now() - gen).total_seconds() < max_hours * 3600:
                        return {'ok': True, 'content': cache.get('report', ''), 'from_cache': True}
            except Exception:
                cache = {}

        # 生成数据
        data = _build_report_data(report_type)

        type_names = {'daily': '日报', 'weekly': '周报', 'monthly': '月报', 'quarterly': '季报', 'yearly': '年报'}
        name = type_names.get(report_type, report_type)

        prompt = (
            f"请根据以下学习数据生成一份{name}（时间范围：{data['date_range']}）：\n"
            f"- 学习时长：{data['total_study_hours']} 小时\n"
            f"- 完成轮次：{data['sessions']} 轮\n"
            f"- 平均复盘质量：{data['avg_quality']}/100\n"
            f"- 高频标签：{', '.join(f'{t}({c})' for t, c in data['top_tags']) or '无'}\n"
            f"- 最近记录：{data['records'][:5]}\n\n"
            f"格式要求：\n"
            f"- 用 ## 标题分节\n"
            f"- 关键数字用 **粗体** 突出\n"
            f"- 用 - 开头的列表项，不要用表格（|...|）\n"
            f"- 每段 2-3 行，简洁\n"
            f"包含：\n"
            f"1. 概览（时长/轮次/质量）\n"
            f"2. 趋势分析\n"
            f"3. 改进建议（3-5条）\n"
            f"4. 亮点总结"
        )

        result = _call_ai(prompt)

        if result.get('ok'):
            report_text = result['content']
            # 持久化缓存
            try:
                cache = {'data': data, 'report': report_text, 'generated_at': datetime.now().isoformat(), 'provider': result.get('provider', '')}
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
            return {'ok': True, 'content': report_text}

        return result

    except Exception as e:
        log.error(f'[generate_report] 报告生成失败: {e}')
        return {'ok': False, 'error': f'报告生成失败：{e}'}


class _ReportWorker(QThread):
    """后台线程：生成 AI 报告，不阻塞 UI"""
    finished = pyqtSignal(dict)

    def __init__(self, parent=None, report_type=None, force_refresh=False):
        super().__init__(parent)
        self.report_type = report_type
        self.force_refresh = force_refresh

    def run(self):
        try:
            result = generate_report(self.report_type, force_refresh=self.force_refresh)
            self.finished.emit(result)
        except Exception as e:
            log.error(f'[ReportWorker] 报告生成异常: {e}')
            self.finished.emit({"ok": False, "error": f"报告生成异常：{e}"})


def _create_app_icon():
    """从 cute_icon.png 加载应用图标（PNG 在任务栏渲染更好）"""
    from PyQt5.QtGui import QPixmap
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.png')
    if os.path.exists(icon_path):
        icon = QIcon(icon_path)
        if not icon.isNull():
            return icon
    # fallback：动态生成 ⚡ 图标
    pm = QPixmap(64, 64)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(212, 175, 55, 30)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, 60, 60)
    painter.setBrush(QBrush(QColor(20, 20, 24)))
    painter.setPen(QPen(QColor(212, 175, 55, 120), 2))
    painter.drawEllipse(6, 6, 52, 52)
    painter.setPen(QColor(212, 175, 55))
    painter.setFont(QFont('Segoe UI Emoji', 22, QFont.Bold))
    painter.drawText(pm.rect(), Qt.AlignCenter, '⚡')
    painter.end()
    icon = QIcon(pm)
    icon.addPixmap(pm.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation), QIcon.Normal, QIcon.Off)
    icon.addPixmap(pm.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation), QIcon.Normal, QIcon.On)
    return icon


class RestReminderWidget(QWidget):
    TAB_NAMES = ['今日', 'AI 报告', '趋势', '设置', '关于']  # 单一来源

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
        sn_key = self.app_settings.get('sensenova_api_key', '')
        ag_key = self.app_settings.get('agnes_api_key', '')
        log.info(f'[AI] sensenova_key={bool(sn_key)} agnes_key={bool(ag_key)}')

        # 5分钟倒计时浮层状态
        self._study_countdown_active = False

        # 计时规则：固定60分钟学习 → 5分钟倒计时 → 5分钟休息 → 固定B站URL
        self._activity_interval = 60  # 固定60分钟
        self._round_count = 0  # 已完成的学习轮数（每轮=1小时学习+5分钟休息）

        # 目标锚点
        today = datetime.now().date().isoformat()
        d = goal_store.load()
        self.goal_text = d.get('goal', '') if d.get('date') == today else ''

        # 快速复盘
        self._pending_review = False


        self.drag_position = None

        # 状态机字段预初始化
        self._rest_end_time = None

        self.init_ui()
        # 创建托盘卡片（浮球点击入口，与主界面分开）
        self._tray_card = TrayCardWidget(self)
        self._tray_card.action_requested.connect(self._on_card_action)
        self._update_tray_card()
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
        if not self.app_settings.get('silent_start', False):
            self.show()
        # 恢复上次运行状态（跨重启续接）
        self._restore_active_state()
        # 启动时提示设目标
        self._prompt_goal()

    def init_ui(self):
        self.setWindowTitle('休息提醒 v4.4')
        self.widget_width = 960
        self.widget_height = 680
        self.setGeometry(100, 100, self.widget_width, self.widget_height)

        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

        self.app_icon = _create_app_icon()
        self.setWindowIcon(self.app_icon)
        self.setObjectName('mainWindow')

        # ═══ 暖墨色系视觉体系 ═══
        #  深炭底 + 琥珀金 accent + 暖灰层次 — 区别于蓝黑模板风
        self.setStyleSheet("""
            QWidget { background-color: #0d0d12; color: #e8e4dc; }
            QWidget#mainWindow {
                background-color: #0d0d12;
                border: 1px solid rgba(255, 255, 255, 0.05);
                border-radius: 14px;
            }
            QLabel { color: #e8e4dc; font-size: 13px; background: transparent; font-family: 'Segoe UI Emoji', 'Microsoft YaHei', sans-serif; }
            /* ── 侧边栏 ── */
            QFrame#sidebar {
                background: #111116;
                border-right: 1px solid #1c1c24;
            }
            QPushButton#navBtn {
                background: transparent; color: #7a7680;
                border: none; border-radius: 8px;
                padding: 10px 14px; font-size: 13px;
                font-family: 'Microsoft YaHei', sans-serif;
                text-align: left; min-height: 44px;
            }
            QPushButton#navBtn:hover { background: rgba(212, 168, 83, 0.08); color: #c4b8a0; }
            QPushButton#navBtn:checked {
                background: rgba(212, 168, 83, 0.12); color: #d4a853;
            }
            /* ── 通用按钮 ── */
            QPushButton {
                background: rgba(255,255,255,0.05); color: #b8b4ac;
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 8px; padding: 8px 16px; font-size: 12px;
                font-family: 'Microsoft YaHei', sans-serif;
            }
            QPushButton:hover { background: rgba(255,255,255,0.10); color: #e8e4dc; }
            QPushButton#accentBtn {
                background: #d4a853; color: #0d0d12; border: none;
                font-weight: bold;
            }
            QPushButton#accentBtn:hover { background: #e8bc6a; }
            QPushButton#dangerBtn { color: #c95454; border-color: rgba(201,84,84,0.20); }
            QPushButton#dangerBtn:hover { background: rgba(201,84,84,0.10); }
            /* ── 输入框 ── */
            QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530;
                border-radius: 8px; padding: 8px 12px; font-size: 12px; }
            QComboBox { background: #16161c; color: #e8e4dc; border: 1px solid #252530;
                border-radius: 8px; padding: 7px 12px; font-size: 12px; min-width: 100px; }
            QComboBox::drop-down { border: none; }
            /* ── 卡片 ── */
            QFrame#statCard {
                background: #18181f; border: 1px solid #252530;
                border-radius: 12px;
            }
            QFrame#sectionCard {
                background: #18181f; border: 1px solid #252530;
                border-radius: 12px;
            }
            /* ── 滚动条 ── */
            QScrollBar:vertical { background: transparent; width: 6px; }
            QScrollBar::handle:vertical { background: #2a2a35; border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: #3a3a48; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            /* ── 分隔线 ── */
            QFrame#divider {
                background: #1c1c24; max-height: 1px; min-height: 1px;
            }
        """)

        # ═══ 根布局：侧边栏 + 主内容 ═══
        root_layout = QHBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ── 侧边栏 ──
        sidebar = QFrame()
        sidebar.setObjectName('sidebar')
        sidebar.setFixedWidth(72)
        sidebar.setCursor(Qt.ArrowCursor)
        sb_layout = QVBoxLayout(sidebar)
        sb_layout.setContentsMargins(8, 12, 8, 12)
        sb_layout.setSpacing(2)

        # Logo / 品牌
        logo = QLabel('⚡')
        logo.setFont(QFont('Segoe UI Emoji', 20))
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet('background: transparent; padding: 4px;')
        sb_layout.addWidget(logo)
        sb_layout.addSpacing(8)

        # 分隔线
        div1 = QFrame()
        div1.setObjectName('divider')
        sb_layout.addWidget(div1)
        sb_layout.addSpacing(8)

        # 导航按钮
        self._tab_buttons = {}
        self._sidebar_icons = {}
        nav_items = [
            ('今日', '📋'),
            ('AI 报告', '🤖'),
            ('趋势', '📈'),
            ('设置', '⚙️'),
            ('关于', 'ℹ'),
        ]
        for name, icon in nav_items:
            btn = QPushButton(f'{icon}\n{name}')
            btn.setObjectName('navBtn')
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(lambda checked, n=name: self._switch_tab(n))
            self._tab_buttons[name] = btn
            self._sidebar_icons[name] = icon
            sb_layout.addWidget(btn)

        sb_layout.addStretch()

        # 底部版本标签
        ver_lbl = QLabel('v4.4')
        ver_lbl.setAlignment(Qt.AlignCenter)
        ver_lbl.setStyleSheet('color: #444; font-size: 10px; font-family: Consolas; background: transparent;')
        sb_layout.addWidget(ver_lbl)

        root_layout.addWidget(sidebar)

        # ── 右侧主内容区 ──
        content_widget = QWidget()
        content_widget.setStyleSheet('background: #0d0d12;')
        main_layout = QVBoxLayout(content_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 顶部标题栏
        top_bar = QWidget()
        top_bar.setFixedHeight(48)
        top_bar.setStyleSheet('background: #0d0d12;')
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(16, 8, 12, 8)

        title = QLabel('休息提醒')
        title.setFont(QFont('Georgia, "Noto Serif SC", serif', 15, QFont.Bold))
        title.setStyleSheet('color: #e8e4dc;')
        top_layout.addWidget(title)

        # 计时器状态徽章
        self._status_badge = QLabel('就绪')
        self._status_badge.setFont(QFont('Microsoft YaHei', 10))
        self._status_badge.setStyleSheet("""
            color: #d4a853; background: rgba(212,168,83,0.10);
            border: 1px solid rgba(212,168,83,0.15);
            border-radius: 6px; padding: 4px 12px;
        """)
        top_layout.addWidget(self._status_badge)
        top_layout.addStretch()

        # 窗口按钮（始终可见，关闭按钮 hover 变红）
        close_style = """
            QPushButton {
                background: transparent; border: none; border-radius: 6px;
                color: #999; font-size: 15px; padding: 2px;
            }
            QPushButton:hover {
                background: rgba(255,80,80,0.20); color: #ff6b6b;
            }
        """
        for sym, slot, tip, style in [
                ('−', self.showMinimized, '最小化', None),
                ('✕', self.close, '关闭', close_style)]:
            b = QPushButton(sym)
            b.setFixedSize(32, 32)
            b.setFont(QFont('Segoe UI Symbol', 13))
            b.setToolTip(tip)
            b.setCursor(Qt.PointingHandCursor)
            if style:
                b.setStyleSheet(style)
            else:
                b.setStyleSheet("""
                    QPushButton {
                        background: transparent; border: none; border-radius: 6px;
                        color: #999; font-size: 15px; padding: 2px;
                    }
                    QPushButton:hover {
                        background: rgba(255,255,255,0.10); color: #fff;
                    }
                """)
            b.clicked.connect(slot)
            top_layout.addWidget(b)

        main_layout.addWidget(top_bar)

        # Tab 内容区
        self._tab_content = QStackedWidget()
        self._tab_content.setStyleSheet('background: #0d0d12; border: none;')
        main_layout.addWidget(self._tab_content)

        # 构建各 tab
        self._build_general_tab()      # index 0: 今日概览
        self._build_ai_tab()            # index 1: AI报告
        self._build_trend_tab()         # index 2: 趋势
        self._build_settings_tab()      # index 3: 设置
        self._build_about_tab()         # index 4: 关于

        root_layout.addWidget(content_widget, 1)
        self.setLayout(root_layout)

        # 默认选中第一个 tab
        self._switch_tab(self.TAB_NAMES[0])

    # ═══ Toggle Switch 组件 ═══
    def _make_toggle(self, checked, callback):
        """创建一个 CC Switch 风格的 toggle 开关"""
        from PyQt5.QtWidgets import QSlider
        slider = QSlider(Qt.Horizontal)
        slider.setFixedWidth(40)
        slider.setFixedHeight(20)
        slider.setMinimum(0)
        slider.setMaximum(1)
        slider.setValue(1 if checked else 0)
        slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #333; border-radius: 10px; height: 20px;
            }
            QSlider::handle:horizontal {
                background: #fff; border-radius: 10px; width: 16px; height: 16px;
                margin: 2px 2px 2px 2px;
            }
            QSlider::sub-page:horizontal {
                background: #3b82f6; border-radius: 10px;
            }
        """)
        slider.valueChanged.connect(callback)
        return slider

    def _make_stat_card(self, icon, title, value, color):
        """统一风格的数据卡片（暴露 _value_label 供刷新）"""
        card = QFrame()
        card.setObjectName('statCard')
        c = QVBoxLayout(card)
        c.setContentsMargins(16, 14, 16, 14)
        c.setSpacing(4)
        icon_lbl = QLabel(icon)
        icon_lbl.setStyleSheet('font-size: 18px; background: transparent;')
        c.addWidget(icon_lbl)
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f'color: {color}; font-size: 16px; font-weight: bold; background: transparent;')
        c.addWidget(val_lbl)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        c.addWidget(title_lbl)
        card._value_label = val_lbl
        return card

    def _make_section_header(self, icon, title):
        """CC Switch 风格分节标题"""
        header = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(18, 18)
        icon_lbl.setStyleSheet('background: transparent;')
        header.addWidget(icon_lbl)
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet('color: #6a8cbb; font-size: 12px; font-weight: bold; font-family: "Microsoft YaHei", sans-serif; background: transparent;')
        header.addWidget(title_lbl)
        header.addStretch()
        return header

    def _make_setting_row(self, icon, title, desc, checked, callback):
        """CC Switch 风格设置行：图标 + 标题/描述 + toggle"""
        row = QFrame()
        row.setObjectName('sectionCard')
        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(14, 12, 14, 12)
        row_layout.setSpacing(10)

        # 图标
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(20, 20)
        icon_lbl.setStyleSheet('background: transparent;')
        row_layout.addWidget(icon_lbl)

        # 标题 + 描述
        text_col = QVBoxLayout()
        text_col.setSpacing(2)
        text_col.setContentsMargins(0, 0, 0, 0)
        t = QLabel(title)
        t.setStyleSheet('color: #e8e6e1; font-size: 13px; font-family: "Microsoft YaHei", sans-serif; background: transparent;')
        text_col.addWidget(t)
        if desc:
            d = QLabel(desc)
            d.setStyleSheet('color: #555; font-size: 11px; font-family: "Microsoft YaHei", sans-serif; background: transparent;')
            text_col.addWidget(d)
        row_layout.addLayout(text_col, 1)

        # toggle
        toggle = self._make_toggle(checked, callback)
        row_layout.addWidget(toggle)
        return row

    def _switch_tab(self, name):
        """切换 tab（侧边栏按钮选中 + stacked widget 切换 + 更新窗口标题）"""
        for n, btn in self._tab_buttons.items():
            btn.setChecked(n == name)
        idx = self.TAB_NAMES.index(name)
        self._tab_content.setCurrentIndex(idx)
        # 更新窗口标题以反映当前 tab
        title_map = {'今日': '📊 今日', 'AI 报告': '🤖 AI 学习报告', '趋势': '📈 学习趋势', '设置': '⚙️ 设置', '关于': 'ℹ️ 关于'}
        self.setWindowTitle(f'休息提醒 v4.4 — {title_map.get(name, name)}')

    def _build_general_tab(self):
        """今日 tab：学习概览 + 今日数据"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 大标题
        h1 = QLabel('今日')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        h1.setStyleSheet('color: #e8e6e1;')
        layout.addWidget(h1)
        sub = QLabel(self._today_subtitle())
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(12)

        # ── 核心数据卡片 ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(10)

        # 学习时长
        study_card = self._make_stat_card('📚', '学习时长', f'{self.study_hours_today:.1f}h', '#d4af37')
        cards_row.addWidget(study_card)

        # 本轮
        round_card = self._make_stat_card('🔥', '当前轮次', f'第 {self._round_count + 1} 轮', '#78B450')
        cards_row.addWidget(round_card)

        # 休息
        break_card = self._make_stat_card('☕', '休息时长', f'{LocalSync.load_break_minutes():.0f}分钟', '#d97757')
        cards_row.addWidget(break_card)

        self._today_refs['study_card'] = study_card
        self._today_refs['round_card'] = round_card
        self._today_refs['break_card'] = break_card

        layout.addLayout(cards_row)
        layout.addSpacing(8)

        # ── 计时状态 ──
        status_card = QFrame()
        status_card.setObjectName('statCard')
        sc = QVBoxLayout(status_card)
        sc.setContentsMargins(16, 14, 16, 14)
        sc.setSpacing(6)
        state_names = {'idle': '⏸ 待机', 'running': '▶ 学习中', 'resting': '☕ 休息中', 'paused': '⏸ 已暂停'}
        state_lbl = QLabel(f'状态：{state_names.get(self.timer_state, self.timer_state)}')
        state_lbl.setObjectName('stateLabel')
        state_lbl.setStyleSheet('color: #e8e6e1; font-size: 14px;')
        sc.addWidget(state_lbl)
        if self.timer_state == 'running' and self.start_time:
            elapsed = (time.time() - self.start_time) / 60
            remaining = max(0, 60 - elapsed)
            timer_lbl = QLabel(f'⏱ 本轮剩余：{remaining:.0f} 分钟')
            timer_lbl.setObjectName('timerLabel')
            timer_lbl.setStyleSheet('color: #6a8cbb; font-size: 12px;')
            sc.addWidget(timer_lbl)
        elif self.timer_state == 'resting' and self.break_start:
            elapsed = (time.time() - self.break_start) / 60
            remaining = max(0, 5 - elapsed)
            timer_lbl = QLabel(f'⏱ 休息剩余：{remaining:.0f} 分钟')
            timer_lbl.setObjectName('timerLabel')
            timer_lbl.setStyleSheet('color: #d97757; font-size: 12px;')
            sc.addWidget(timer_lbl)
        layout.addWidget(status_card)
        layout.addSpacing(8)

        # ── 距离22:00倒计时 ──
        countdown_card = QFrame()
        countdown_card.setObjectName('statCard')
        cc = QVBoxLayout(countdown_card)
        cc.setContentsMargins(16, 14, 16, 14)
        cc.setSpacing(6)
        cd_title = QLabel('⏳ 距离22:00')
        cd_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold;')
        cc.addWidget(cd_title)
        cd_bar = QProgressBar()
        cd_bar.setObjectName('countdownBar')
        cd_bar.setMaximum(100)
        cd_bar.setValue(0)
        cd_bar.setTextVisible(True)
        cd_bar.setFormat('%p%')
        cd_bar.setFixedHeight(16)
        cd_bar.setStyleSheet("""
            QProgressBar { background: rgba(255,255,255,0.06); border: none; border-radius: 4px; }
            QProgressBar::chunk { background: qlineargradient(x1:0,x2:1,stop:0 #FF9800,stop:1 #FF5252); border-radius: 4px; }
        """)
        cc.addWidget(cd_bar)
        cd_time = QLabel('')
        cd_time.setStyleSheet('color: #888; font-size: 11px;')
        cc.addWidget(cd_time)
        self._cd_bar = cd_bar
        self._cd_time = cd_time
        self._update_countdown_display()
        log.info('[CountdownCard] 距离22:00卡片已构建')
        layout.addWidget(countdown_card)
        self._today_refs['cd_bar'] = cd_bar
        self._today_refs['cd_time'] = cd_time
        layout.addSpacing(8)

        # ── 复盘摘要 ──
        reviews_data = review_store.load()
        today_reviews = reviews_data.get(datetime.now().date().isoformat(), [])
        if today_reviews:
            info = _review_summary(today_reviews)
            sufx = '⭐' if info['is_old'] else '分'
            review_card = QFrame()
            review_card.setObjectName('statCard')
            rc = QVBoxLayout(review_card)
            rc.setContentsMargins(16, 14, 16, 14)
            rc.setSpacing(4)
            rc_title = QLabel(f'📊 今日复盘：{info["count"]} 次 · 平均 {info["avg"]:.1f}{sufx}')
            rc_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold;')
            rc.addWidget(rc_title)
            b = info['best']; w = info['worst']
            if b and w:
                rc_detail = QLabel(f'🏆 最佳 {b["score"]}{sufx} ({b["time"]})  ⚠️ 最低 {w["score"]}{sufx} ({w["time"]})')
            else:
                rc_detail = QLabel(f'🏆 平均 {info["avg"]:.1f}{sufx}')
            rc_detail.setStyleSheet('color: #888; font-size: 11px;')
            rc.addWidget(rc_detail)
            layout.addWidget(review_card)
            layout.addSpacing(8)

        # ── 连续打卡 ──
        streak = LocalSync.load_streak()
        streak_card = self._make_stat_card('🔥', '连续打卡', f'{streak["current_streak"]} 天（最佳 {streak["best_streak"]} 天）', '#d4af37')
        # 今日 tab 显示元素引用（供 update_display 每秒刷新）
        self._today_refs = {}

        layout.addWidget(streak_card)
        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

    def _today_subtitle(self):
        """今日 tab 副标题"""
        now = datetime.now()
        if now.hour >= 22:
            return '今天的学习已经结束，好好休息'
        state_names = {'idle': '准备好开始学习了吗？', 'running': '保持专注，你正在进步', 'resting': '放松一下，马上回来', 'paused': '已暂停，随时可以继续'}
        return state_names.get(self.timer_state, '精力管理，从今天开始')
    def _toggle_silent_start(self, checked):
        self.app_settings['silent_start'] = checked == 1
        LocalSync.save_settings(self.app_settings)

    def _toggle_close_to_tray(self, checked):
        self.app_settings['close_to_tray'] = checked == 1
        LocalSync.save_settings(self.app_settings)

    def _toggle_study_tracking(self, checked):
        self.app_settings['study_tracking'] = checked == 1
        LocalSync.save_settings(self.app_settings)

    def _toggle_review_reminder(self, checked):
        self.app_settings['review_reminder'] = checked == 1
        LocalSync.save_settings(self.app_settings)

    def _toggle_sound(self, checked):
        self.app_settings['sound_enabled'] = checked == 1
        LocalSync.save_settings(self.app_settings)

    def _build_ai_tab(self):
        """AI 报告 tab：5种报告直接展示，点选即生成"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(10)

        h1 = QLabel('AI 学习报告')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        layout.addWidget(h1)
        sub = QLabel('智能分析你的学习节奏和专注模式')
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(8)

        # 5种报告按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._report_buttons = {}
        for label, rtype in [('日报', 'daily'), ('周报', 'weekly'), ('月报', 'monthly'),
                              ('季报', 'quarterly'), ('年报', 'yearly')]:
            b = QPushButton(label)
            b.setCursor(Qt.PointingHandCursor)
            b.setCheckable(True)
            b.setStyleSheet("""
                QPushButton {
                    background: rgba(212,175,55,0.08); color: #999;
                    border: 1px solid #2a2a35; border-radius: 100px;
                    padding: 8px 18px; font-size: 13px;
                }
                QPushButton:checked {
                    background: rgba(212,175,55,0.18); color: #d4af37;
                    border-color: rgba(212,175,55,0.3);
                }
                QPushButton:hover { background: rgba(212,175,55,0.14); color: #ccc; }
            """)
            b.clicked.connect(lambda checked, t=rtype: self._load_report(t))
            btn_row.addWidget(b)
            self._report_buttons[rtype] = b
        layout.addLayout(btn_row)
        layout.addSpacing(6)

        # 报告内容区
        self._report_view = QTextBrowser()
        self._report_view.setOpenExternalLinks(True)
        self._report_view.setStyleSheet("""
            QTextBrowser {
                background: #14141a; color: #e8e6e1;
                border: 1px solid #222; border-radius: 8px;
                padding: 16px; font-size: 13px; line-height: 1.7;
            }
        """)
        layout.addWidget(self._report_view, 1)

        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)
        # 默认选中日报
        QTimer.singleShot(100, lambda: self._load_report('daily'))

    def _load_report(self, report_type, force_refresh=False):
        """加载并显示 AI 报告（后台线程，不阻塞 UI）"""
        for t, b in self._report_buttons.items():
            b.setChecked(t == report_type)
        self._report_view.setHtml('<p style="color:#888;">⏳ 正在生成报告...</p>')
        QApplication.processEvents()

        # 禁用按钮防止重复点击
        for b in self._report_buttons.values():
            b.setEnabled(False)

        worker = _ReportWorker(self, report_type, force_refresh)
        def _on_done(result):
            for b in self._report_buttons.values():
                b.setEnabled(True)
            if result.get("ok"):
                self._report_view.setHtml(_md_to_html(result['content']))
            elif result.get("error"):
                self._report_view.setHtml(f'<p style="color:#c95454;">⚠️ AI 请求失败: {result["error"]}</p><p style="color:#888;">点击「刷新」重试。</p>')
        worker.finished.connect(_on_done)
        worker.start()

    def _build_trend_tab(self):
        """趋势 tab：内嵌趋势图（不弹窗）"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        h1 = QLabel('学习趋势')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        layout.addWidget(h1)
        sub = QLabel('可视化你的学习节奏和专注度')
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(8)

        # 内嵌小型趋势图（复用 TrendWindow 的数据逻辑，简化显示）
        trend_card = QFrame()
        trend_card.setObjectName('statCard')
        tc_layout = QVBoxLayout(trend_card)
        tc_layout.setContentsMargins(16, 14, 16, 14)
        tc_layout.setSpacing(8)

        # 7天迷你柱图
        mini_chart = QWidget()
        mini_chart.setFixedHeight(160)
        mini_chart.setStyleSheet('background: transparent;')
        from datetime import timedelta
        today = datetime.now().date()
        days = []
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            data = history_store.load().get(d, {})
            days.append({'label': (today - timedelta(days=i)).strftime('%m/%d'),
                         'study': data.get('study', 0)})

        def paint_mini(e):
            p = QPainter(mini_chart)
            p.setRenderHint(QPainter.Antialiasing)
            w, h = mini_chart.width(), mini_chart.height()
            n = len(days)
            if n == 0: return
            vals = [d['study'] for d in days]
            mx = max(max(vals, default=0), 1)
            bw = min(22, int((w - 40) / (n + 1)))
            gap = int((w - 40 - n * bw) / (n + 1))
            bottom = h - 28
            ch = bottom - 8
            mini_chart._bar_rects = []
            for i, d in enumerate(days):
                x = 20 + gap + i * (bw + gap)
                bh = int(d['study'] / mx * ch)
                p.setBrush(QBrush(QColor('#788C57')))
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(x, bottom - bh, bw, bh, 2, 2)
                mini_chart._bar_rects.append((QRect(x, bottom - bh, bw, bh), d['label'], d['study']))
                p.setPen(QColor('#666'))
                p.setFont(QFont('Microsoft YaHei', 8))
                p.drawText(x + bw // 2 - 8, bottom + 14, d['label'])
                if d['study'] > 0:
                    p.setPen(QColor('#788C57'))
                    p.drawText(x + bw // 2 - 8, bottom - bh - 4, f"{d['study']:.1f}")
        mini_chart.paintEvent = paint_mini

        def on_mini_move(e):
            pos = e.pos()
            for rect, label, value in mini_chart._bar_rects:
                if rect.contains(pos):
                    QToolTip.showText(mini_chart.mapToGlobal(e.pos()), f'{label} 学习 {value:.1f}h', mini_chart, rect, 2000)
                    return
            QToolTip.hideText()
        mini_chart.mouseMoveEvent = on_mini_move
        mini_chart.setMouseTracking(True)
        tc_layout.addWidget(mini_chart)
        # 强制触发 paintEvent（QScrollArea 内嵌 widget 不会自动触发）
        mini_chart.update()

        # 图例
        legend = QLabel('🟢 学习时长')
        legend.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        tc_layout.addWidget(legend)

        # 总计
        ts = sum(d['study'] for d in days)
        summary = QLabel(f'近7天 · 学习 {ts:.1f}h')
        summary.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        tc_layout.addWidget(summary)
        layout.addWidget(trend_card)

        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

    def _build_settings_tab(self):
        """设置 tab：所有 toggle 开关"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        h1 = QLabel('设置')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        layout.addWidget(h1)
        sub = QLabel('管理计时器、提醒方式和基础设置')
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(12)

        # ═══ 窗口行为 ═══
        layout.addLayout(self._make_section_header('🪟', '窗口行为'))

        autostart_checked = self.is_autostart_enabled()
        silent_checked = self.app_settings.get('silent_start', False)
        close_tray_checked = self.app_settings.get('close_to_tray', True)
        study_checked = self.app_settings.get('study_tracking', True)
        review_checked = self.app_settings.get('review_reminder', True)
        sound_checked = self.app_settings.get('sound_enabled', True)

        autostart_row = self._make_setting_row(
            '⚡', '开机自启',
            '随系统启动自动运行精力管理',
            autostart_checked,
            lambda v: self.set_autostart(v == 1)
        )
        layout.addWidget(autostart_row)

        silent_row = self._make_setting_row(
            '👻', '静默启动',
            '程序启动时不显示主窗口，仅在系统托盘运行',
            silent_checked,
            self._toggle_silent_start
        )
        layout.addWidget(silent_row)

        close_tray_row = self._make_setting_row(
            '📦', '关闭时最小化到托盘',
            '点击关闭按钮时隐藏到系统托盘，不退出程序',
            close_tray_checked,
            self._toggle_close_to_tray
        )
        layout.addWidget(close_tray_row)

        # ═══ 计时设置 ═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('⏱️', '计时设置'))

        study_row = self._make_setting_row(
            '📚', '学习时长统计',
            '每次倒计时完成自动记录 1 小时学习时长',
            study_checked,
            self._toggle_study_tracking
        )
        layout.addWidget(study_row)

        review_row = self._make_setting_row(
            '⭐', '复盘提醒',
            '每小时休息前弹出复盘评分（1-100分）',
            review_checked,
            self._toggle_review_reminder
        )
        layout.addWidget(review_row)

        sound_row = self._make_setting_row(
            '🔔', '声音提醒',
            '倒计时结束时播放提示音',
            sound_checked,
            self._toggle_sound
        )
        layout.addWidget(sound_row)

        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

    def _build_about_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        h1 = QLabel('关于')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        layout.addWidget(h1)
        sub = QLabel('查看版本信息与更新状态。')
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(8)

        # ── 产品卡片（logo + 版本 + 操作按钮） ──
        app_card = QFrame()
        app_card.setObjectName('statCard')
        ac = QVBoxLayout(app_card)
        ac.setContentsMargins(20, 18, 20, 18)
        ac.setSpacing(12)

        # 顶部：图标 + 名称 + 版本
        top_row = QHBoxLayout()
        icon_lbl = QLabel('⚡')
        icon_lbl.setFont(QFont('Segoe UI Emoji', 24))
        icon_lbl.setStyleSheet('background: transparent;')
        top_row.addWidget(icon_lbl)
        name_lbl = QLabel('精力管理')
        name_lbl.setFont(QFont('Georgia, "Noto Serif SC", serif', 16, QFont.Bold))
        name_lbl.setStyleSheet('color: #e8e6e1;')
        top_row.addWidget(name_lbl)
        # 版本 badge
        ver_badge = QLabel('v4.4')
        ver_badge.setStyleSheet('background: rgba(255,255,255,0.08); color: #888; border-radius: 6px; padding: 3px 10px; font-size: 11px; font-family: Consolas;')
        top_row.addWidget(ver_badge)
        top_row.addStretch()
        ac.addLayout(top_row)

        desc_lbl = QLabel('开源 MIT · 桌面休息提醒挂件')
        desc_lbl.setStyleSheet('color: #666; font-size: 12px;')
        ac.addWidget(desc_lbl)

        # 操作按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        for text, slot in [
            ('🌐 官方网站', self._open_website),
            ('🐱 GitHub', self._open_github),
            ('📋 更新日志', self._show_changelog),
            ('🔄 检查更新', self._check_update),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        ac.addLayout(btn_row)

        layout.addWidget(app_card)
        layout.addSpacing(8)

        # ── 本地环境检查 ──
        env_title = QLabel('本地环境检查')
        env_title.setFont(QFont('Georgia, "Noto Serif SC", serif', 14, QFont.Bold))
        layout.addWidget(env_title)

        env_card = QFrame()
        env_card.setObjectName('sectionCard')
        ec = QVBoxLayout(env_card)
        ec.setContentsMargins(16, 14, 16, 14)
        ec.setSpacing(8)

        # 刷新按钮行
        env_btn_row = QHBoxLayout()
        env_btn_row.setSpacing(8)
        for text, slot in [
            ('🔍 诊断安装冲突', self._diagnose_env),
            ('🔄 刷新', self._refresh_env_check),
            ('⬆️ 全部升级', self._upgrade_all),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(slot)
            env_btn_row.addWidget(btn)
        env_btn_row.addStretch()
        ec.addLayout(env_btn_row)

        # 环境项（Python / PyQt5 / 平台）
        for name, check_fn in [
            ('Python', self._check_python),
            ('PyQt5', self._check_pyqt5),
            ('平台', self._check_platform),
        ]:
            row = QHBoxLayout()
            row.setSpacing(8)
            icon = QLabel('◆')
            icon.setStyleSheet('color: #555; font-size: 10px; background: transparent;')
            icon.setFixedWidth(16)
            row.addWidget(icon)
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet('color: #888; font-size: 12px;')
            name_lbl.setFixedWidth(60)
            row.addWidget(name_lbl)
            version_lbl = QLabel('检测中...')
            version_lbl.setStyleSheet('color: #6a8cbb; font-size: 12px; font-family: Consolas;')
            version_lbl.setObjectName(f'env_{name}')
            row.addWidget(version_lbl)
            row.addStretch()
            refresh_btn = QPushButton('⟳')
            refresh_btn.setFixedSize(24, 24)
            refresh_btn.setStyleSheet('background: transparent; border: none; color: #555; font-size: 14px;')
            refresh_btn.clicked.connect(check_fn)
            row.addWidget(refresh_btn)
            ec.addLayout(row)

        layout.addWidget(env_card)

        # 延迟检测（等 UI 渲染完）
        QTimer.singleShot(100, self._refresh_env_check)

        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

    # ── About 页辅助方法 ──
    def _open_website(self):
        open_url('https://crazy-rest-reminder.pages.dev')

    def _open_github(self):
        open_url('https://github.com/kuangketongxue/library-remind')

    def _show_changelog(self):
        """显示更新日志"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
        dialog = QDialog(self)
        dialog.setWindowTitle('📋 更新日志')
        dialog.setFixedSize(500, 400)
        dialog.setStyleSheet("""
            QDialog { background-color: #0c0c10; color: #e8e6e1; }
            QTextBrowser { background: #14141a; color: #e8e6e1; border: 1px solid #222; border-radius: 8px; padding: 12px; font-size: 13px; font-family: Consolas; }
        """)
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setPlainText('''v4.3 (2026-06-21)
━━━━━━━━━━━━━━━━
• 重新设计主界面：5 tab 结构（今日 / AI 报告 / 趋势 / 设置 / 关于）
• 浮球独立：60×60 ⏰ 图标 + 点击弹出 info 浮层
• 修复趋势 tab 快速点击数据丢失问题
• 删除空壳 tab（路由/认证/高级）
• 计时规则变更：60分钟学习→5分钟休息→固定B站收藏夹
• 新增趋势 tab 内嵌 7 天迷你柱图

v4.2 (2026-06-18)
━━━━━━━━━━━━━━━━
• AI 报告：日报/周报/月报/季报/年报
• TTS 语音播报报告
• 缓存系统
• Anthropic 风格界面

v4.1 (2026-06-17)
━━━━━━━━━━━━━━━━
• 首次公开发布
• 基础番茄钟 + 休息提醒
• B站收藏夹自动播放
• 系统托盘支持''')
        layout.addWidget(browser)
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        dialog.exec_()

    def _check_update(self):
        """检查更新（打开官网查看最新版本）"""
        open_url('https://crazy-rest-reminder.pages.dev')
        self.tray_icon.showMessage('检查更新', '请在浏览器中查看最新版本', QSystemTrayIcon.Information, 3000)

    # ── 环境检查辅助方法 ──
    def _refresh_env_check(self):
        """刷新所有环境检测"""
        self._check_python()
        self._check_pyqt5()
        self._check_platform()

    def _check_python(self):
        lbl = self.findChild(QLabel, 'env_Python')
        if lbl:
            lbl.setText(f'{platform.python_version()}')

    def _check_pyqt5(self):
        lbl = self.findChild(QLabel, 'env_PyQt5')
        if lbl:
            try:
                from PyQt5.QtCore import QT_VERSION_STR
                lbl.setText(f'PyQt5 {QT_VERSION_STR}')
            except ImportError:
                lbl.setText('未安装')
                lbl.setStyleSheet('color: #ff4444; font-size: 12px; font-family: Consolas;')

    def _check_platform(self):
        lbl = self.findChild(QLabel, 'env_平台')
        if lbl:
            lbl.setText(f'{platform.system()} {platform.machine()}')

    def _diagnose_env(self):
        """诊断安装冲突"""
        from PyQt5.QtWidgets import QMessageBox
        issues = []
        try:
            import PyQt5
            issues.append(f'✅ PyQt5 {PyQt5.QT_VERSION_STR}')
        except ImportError:
            issues.append('❌ PyQt5 未安装')
        try:
            import requests
            issues.append(f'✅ requests {requests.__version__}')
        except ImportError:
            issues.append('❌ requests 未安装')
        try:
            import psutil
            issues.append(f'✅ psutil {psutil.__version__}')
        except ImportError:
            issues.append('❌ psutil 未安装')
        QMessageBox.information(self, '环境诊断', '\n'.join(issues))

    def _upgrade_all(self):
        """全部升级（打开 pip 升级命令）"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, '全部升级',
            '请在终端运行：\npip install --upgrade PyQt5 requests psutil')

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
            self._trend_window.destroyed.connect(lambda: setattr(self, '_trend_window', None))
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
        # PyInstaller 打包：_MEI 临时目录不可持久化，需回退到源目录
        script = os.path.abspath(__file__)
        if getattr(sys, 'frozen', False):
            # 打包模式下用 _launch.vbs（固定路径），不走 __file__
            script_dir = os.path.dirname(os.path.abspath(sys.executable))
            script = os.path.join(script_dir, 'rest_reminder.py')
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
        """切换自启动（托盘卡片入口）"""
        new_state = not self.is_autostart_enabled()
        if self.set_autostart(new_state):
            tip = '已开启' if new_state else '已关闭'
            self.tray_icon.showMessage('休息提醒', f'开机自启动{tip}', QSystemTrayIcon.Information, 2000)

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
        open_url("https://crazy-rest-reminder.pages.dev")

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

    def _update_tray_card(self):
        """刷新托盘卡片数据"""
        try:
            if hasattr(self, '_tray_card'):
                self._tray_card.update_data(
                    study_hours=self.study_hours_today,
                    streak=self.streak_data.get('current_streak', 0),
                    break_minutes=int(self.break_minutes_today),
                    autostart=self.is_autostart_enabled(),
                    reminder_mode=self.app_settings.get('reminder_mode', 'video'),
                )
        except Exception as e:
            log.error(f'[_update_tray_card 异常] {type(e).__name__}: {e}')

    def _on_card_action(self, action):
        """处理托盘卡片的 action 信号"""
        try:
            if action == 'toggle_visibility':
                self.toggle_visibility()
            elif action == 'toggle_autostart':
                self.toggle_autostart()
            elif action == 'set_mode:video':
                self._set_reminder_mode('video')
            elif action == 'set_mode:quote':
                self._set_reminder_mode('quote')
            elif action == 'set_mode:notify':
                self._set_reminder_mode('notify')
            elif action == 'set_mode:none':
                self._set_reminder_mode('none')
            elif action == 'show_stats':
                self.show_stats()
            elif action == 'set_goal':
                self._show_goal_dialog()
            elif action == 'export_data':
                self.export_weekly_data()
            elif action == 'quit_app':
                self.quit_app()
        except Exception as e:
            log.error(f'[_on_card_action] 处理 {action} 失败: {type(e).__name__}: {e}')

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


    def _sync_buttons(self):
        """同步浮球 popup 按钮状态（旧 start_btn/pause_btn 已移除）"""
        try:
            # 旧 UI 按钮已不存在，仅更新浮球 popup 文字
            ball = getattr(self, 'floating_ball', None)
            if ball and hasattr(ball, '_update_popup_text'):
                ball._update_popup_text()
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
            if self._day_ended:
                self.tray_icon.showMessage('⏰ 今日已结束', '22:00 后不再开始新轮次，明天见！', QSystemTrayIcon.Information, 3000)
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

    @property
    def _day_ended(self):
        """22:00 后自动结束，无需手动设置"""
        return datetime.now().hour >= 22

    def _handle_idle(self):
        """处理空闲状态 - 托盘提示 + popup 更新"""
        self._sync_buttons()
        self.tray_icon.setToolTip(f'⚡ 精力管理 · 续航 {self._activity_interval}min')

    def _handle_running(self, now):
        """处理运行状态 - 固定60分钟倒计时 -> 5分钟请辨 -> 5分钟休息"""
        elapsed = (now - self.start_time).total_seconds()
        total_seconds = 60 * 60  # 固定60分钟
        remaining = max(total_seconds - elapsed, 0)

        mins = int(remaining // 60)
        secs = int(remaining % 60)
        self._sync_buttons()  # display handled by FloatingBall popup
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
                fid = self.app_settings.get('bilibili_fid', '3648313921')
                mid = self.app_settings.get('bilibili_mid', '529362421')
                fav_url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create&spm_id_from=333.788.0.0'
                open_url(fav_url)

            # 弹出本轮目标（非阻塞，3秒自动提交）
            self._prompt_round_goal()

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
            # 显示休息倒计时（通过 popup）
            self._sync_buttons()
            remaining = (self._rest_end_time - now).total_seconds()
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            self.tray_icon.setToolTip(f'⚡ 精力管理 · 休息中 {mins}:{secs:02d}')

    def _handle_paused(self, now):
        """处理暂停状态 - 托盘提示 + popup 更新"""
        self._sync_buttons()
        self.tray_icon.setToolTip('⚡ 精力管理 · ⏸ 已暂停')
        if self._study_countdown_active:
            self._study_countdown_active = False
            self.countdown_overlay.hide_overlay()

    def _update_countdown(self, now):
        """每日汇报提醒（每天只弹一次）"""
        if now.hour >= 22 and not self._daily_report_shown_today:
            self._daily_report_shown_today = True
            study = self.study_hours_today
            msg = f'今日学习：{study} 小时\n\n'
            reviews_data = review_store.load()
            today_reviews = reviews_data.get(datetime.now().date().isoformat(), [])
            if today_reviews:
                info = _review_summary(today_reviews)
                sufx = '⭐' if info['is_old'] else '分'
                avg = info['avg']
                msg += f'📊 复盘 {info["count"]} 次 · 平均 {avg:.1f}{sufx}\n'
                b = info['best']; w = info['worst']
                msg += f'🏆 最佳: {b["time"]}({b["score"]}{sufx}) · ⚠️ 待改进: {w["time"]}({w["score"]}{sufx})\n'
                # 昨日对比
                y_avg = self._load_yesterday_review_avg(reviews_data)
                if y_avg is not None:
                    diff = avg - y_avg
                    arrow = '📈' if diff > 0 else '📉' if diff < 0 else '➡️'
                    msg += f'{arrow} 比昨日 {("+" if diff > 0 else "")}{diff:.1f}{sufx}\n'
            else:
                msg += '📝 今天还没有复盘记录\n'
            msg += '\n记得记录到飞书～'
            self.tray_icon.showMessage('📋 每日记录提醒', msg, QSystemTrayIcon.Information, 8000)
            log.info(f'[DailyReport] 22:00 提醒: 学习{study}h')
            # 检查连续打卡
            self._check_streak()

    def _update_countdown_display(self):
        """更新今日tab中距离22:00的倒计时进度条（4:30=0%, 22:00=100%）"""
        bar = getattr(self, '_cd_bar', None)
        lbl = getattr(self, '_cd_time', None)
        if bar is None or lbl is None or sip.isdeleted(bar) or sip.isdeleted(lbl):
            return
        now = datetime.now()
        midnight = now.replace(hour=0, minute=0, second=0, microsecond=0)
        span_start = int(4.5 * 3600)  # 4:30 = 16200秒
        total_span = int(22 * 3600 - 4.5 * 3600)  # 63000秒
        if now.hour >= 22:
            bar.setValue(100)
            lbl.setText('今天的学习已结束')
        else:
            seconds_since_midnight = (now - midnight).total_seconds()
            if seconds_since_midnight < span_start:
                bar.setValue(0)
                lbl.setText(f'剩余 {22 - now.hour - 1}小时{60 - now.minute}分钟')
            else:
                progress = int(((seconds_since_midnight - span_start) / total_span) * 100)
                bar.setValue(min(progress, 100))
                remaining = 22 * 3600 - seconds_since_midnight
                h = int(remaining // 3600)
                m = int((remaining % 3600) // 60)
                lbl.setText(f'剩余 {h}小时{m}分钟')

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
                self._round_count = 0
                self._activity_interval = 60
                self.break_start = None
                self._study_countdown_active = False
                self.countdown_overlay.hide_overlay()
                self.current_date = now.date()
                self._daily_report_shown_today = False
                LocalSync.reset()
                self.break_minutes_today = 0
                LocalSync.save_break_minutes(0)
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
            self._update_countdown_display()

            # --- 刷新今日 tab 动态内容 ---
            self._refresh_general_tab()

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

            # --- 同步浮球数据（_sync_buttons 已在各状态 handler 中调用） ---

        except Exception as e:
            log.error(f'[update_display 异常] {type(e).__name__}: {e}')
            traceback.print_exc()

    def update_study_display(self):
        """更新通用 tab 中的数据标签"""
        if hasattr(self, 'study_info_label'):
            self.study_info_label.setText(f'{self.study_hours_today:.1f}h')

    def _refresh_general_tab(self):
        """每秒刷新今日 tab 中的动态元素（数据卡片 + 状态 + 倒计时）"""
        try:
            refs = getattr(self, '_today_refs', {})
            if not refs:
                return

            # 数据卡片
            sc = refs.get('study_card')
            if sc and hasattr(sc, '_value_label'):
                sc._value_label.setText(f'{self.study_hours_today:.1f}h')

            rc = refs.get('round_card')
            if rc and hasattr(rc, '_value_label'):
                rc._value_label.setText(f'第 {self._round_count + 1} 轮')

            bc = refs.get('break_card')
            if bc and hasattr(bc, '_value_label'):
                bc._value_label.setText(f'{int(self.break_minutes_today)} 分钟')

            # 状态标签
            state_lbl = self.findChild(QLabel, 'stateLabel')
            if state_lbl and not sip.isdeleted(state_lbl):
                state_names = {'idle': '⏸ 待机', 'running': '▶ 学习中', 'resting': '☕ 休息中', 'paused': '⏸ 已暂停'}
                state_lbl.setText(f'状态：{state_names.get(self.timer_state, self.timer_state)}')

            # 倒计时显示由 _update_countdown_display 统一处理（已在 update_display 调用）
        except (RuntimeError, Exception):
            pass  # WA_DeleteOnClose 后 C++ 对象已销毁

    def _build_review_dialog(self, title, label):
        """构建复盘评分对话框：学科6选1 + 标签5选1 + 评分滑块1-100，1分钟自动提交，金色选中态"""
        parent = self.window() or self
        dialog = QDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setFixedSize(480, 420)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标签
        layout.addWidget(QLabel(label))
        layout.addSpacing(6)

        # 学科按钮组（大按钮，金色选中态）
        layout.addWidget(QLabel('📚 学科：'))
        subject_layout = QHBoxLayout()
        subject_layout.setSpacing(6)
        subject_btns = []
        subject_val = ['未记录']
        for subj in _SUBJECTS:
            btn = QPushButton(subj)
            btn.setCheckable(True)
            btn.setFixedSize(56, 36)
            btn.setStyleSheet("""
                QPushButton { background: #1e1e26; color: #b8b4ac; border: 1px solid #252530; border-radius: 8px; font-size: 12px; }
                QPushButton:checked { background: #d4a853; color: #0d0d12; border: none; font-weight: bold; }
                QPushButton:hover:!checked { background: #2a2a35; }
            """)
            subject_btns.append(btn)
            subject_layout.addWidget(btn)
            def _make_subj_handler(s, sv, b):
                def handler(checked):
                    if checked:
                        sv[0] = s
                        for bb in subject_btns:
                            if bb is not b:
                                bb.blockSignals(True)
                                bb.setChecked(False)
                                bb.blockSignals(False)
                    else:
                        if sv[0] == s:
                            sv[0] = '未记录'
                return handler
            btn.clicked.connect(_make_subj_handler(subj, subject_val, btn))
        layout.addLayout(subject_layout)

        # 标签按钮组（金色选中态）
        layout.addWidget(QLabel('🏷️ 标签：'))
        label_layout = QHBoxLayout()
        label_layout.setSpacing(6)
        label_btns = []
        label_val = ['未记录']
        for lbl in _LABELS:
            btn = QPushButton(lbl)
            btn.setCheckable(True)
            btn.setFixedSize(56, 36)
            btn.setStyleSheet("""
                QPushButton { background: #1e1e26; color: #b8b4ac; border: 1px solid #252530; border-radius: 8px; font-size: 12px; }
                QPushButton:checked { background: #d4a853; color: #0d0d12; border: none; font-weight: bold; }
                QPushButton:hover:!checked { background: #2a2a35; }
            """)
            label_btns.append(btn)
            label_layout.addWidget(btn)
            def _make_lbl_handler(l, lv, b):
                def handler(checked):
                    if checked:
                        lv[0] = l
                        for bb in label_btns:
                            if bb is not b:
                                bb.blockSignals(True)
                                bb.setChecked(False)
                                bb.blockSignals(False)
                    else:
                        if lv[0] == l:
                            lv[0] = '未记录'
                return handler
            btn.clicked.connect(_make_lbl_handler(lbl, label_val, btn))
        layout.addLayout(label_layout)

        # 评分滑块
        layout.addWidget(QLabel('评分：'))
        slider_layout = QHBoxLayout()
        score_slider = QSlider(Qt.Horizontal)
        score_slider.setRange(0, 100)
        score_slider.setValue(50)
        score_slider.setTickPosition(QSlider.TicksBelow)
        score_slider.setTickInterval(10)
        score_label = QLabel('50')
        score_slider.valueChanged.connect(lambda v: score_label.setText(str(v)))
        slider_layout.addWidget(score_slider, 1)
        slider_layout.addWidget(score_label, 0)
        layout.addLayout(slider_layout)

        # 信息栏 + 倒计时
        info_bar = QWidget()
        info_bar.setStyleSheet('background: #16161c; border-radius: 6px;')
        info_layout = QHBoxLayout(info_bar)
        info_layout.setContentsMargins(10, 6, 10, 6)
        info_lbl = QLabel(f'⏳ {AUTO_SUBMIT_SECONDS}秒后自动提交')
        info_lbl.setStyleSheet('color: #666; font-size: 11px; background: transparent;')
        info_layout.addWidget(info_lbl)
        layout.addWidget(info_bar)

        # 提交按钮
        submit_btn = QPushButton('提交复盘')
        submit_btn.clicked.connect(dialog.accept)
        layout.addWidget(submit_btn)

        # 倒计时自动提交
        remaining = [AUTO_SUBMIT_SECONDS]
        def _countdown():
            remaining[0] -= 1
            if remaining[0] > 0:
                info_lbl.setText(f'⏳ {remaining[0]}秒后自动提交')
                QTimer.singleShot(1000, _countdown)
            else:
                info_lbl.setText('⏳ 自动提交中...')
                dialog.accept()
        QTimer.singleShot(1000, _countdown)

        dialog._subject_val = subject_val
        dialog._label_val = label_val
        dialog._score_slider = score_slider
        return dialog

    def _prompt_review(self):
        """快速复盘弹窗：学科+标签+评分1-100（阻塞，60秒自动提交）"""
        try:
            if not self._pending_review:
                return
            dialog = self._build_review_dialog('📝 快速复盘', '这小时学了什么？')
            QTimer.singleShot(AUTO_SUBMIT_SECONDS * 1000, dialog.accept)
            if dialog.exec_():
                subject = dialog._subject_val[0]
                label = dialog._label_val[0]
                score = dialog._score_slider.value()
                self._record_review(score, subject, label)
        except Exception as e:
            log.error(f'[复盘] 弹窗异常: {e}')

    def _record_review(self, score, subject='未记录', label='未记录'):
        """记录自评分数（持久化到 .review_log.json）"""
        if not self._pending_review:
            return
        self._pending_review = False
        log.info(f'[复盘] 本周期评分: {score}/100 | {subject} | {label}')
        self._write_review(score, subject, label)

    def _catchup_review(self):
        """补录复盘：托盘菜单入口"""
        dialog = self._build_review_dialog('📝 补录复盘', '刚才（漏掉的）那小时学得怎么样？')
        QTimer.singleShot(AUTO_SUBMIT_SECONDS * 1000, dialog.accept)
        if dialog.exec_():
            subject = dialog._subject_val[0]
            label = dialog._label_val[0]
            score = dialog._score_slider.value()
            self._write_review(score, subject, label)
            self.tray_icon.showMessage('📝 已补录', f'{score}分 | {subject} | {label}', QSystemTrayIcon.Information, 2000)

    def _write_review(self, score, subject='未记录', label='未记录'):
        """写入复盘记录到文件（供正常复盘和补录共用）"""
        try:
            data = review_store.load()
            today = datetime.now().date().isoformat()
            if today not in data:
                data[today] = []
            data[today].append({
                'time': datetime.now().strftime('%H:%M'),
                'subject': subject,
                'label': label,
                'score': score
            })
            review_store.save(data)
            log.info(f'[复盘] 已记录: {score}/100 | {subject} | {label}')
        except Exception as e:
            log.error(f'[复盘] 保存失败: {e}')

    def _prompt_goal(self):
        """启动时弹出目标选择（只弹一次）"""
        if self.goal_text:
            return
        try:
            self._show_goal_dialog()
        except Exception as e:
            log.error(f'[目标] 提示异常: {e}')

    def _show_goal_dialog(self, event=None):
        """显示目标设置对话框：自由文本 + 预计轮次（event 参数用于 mousePressEvent 回调）"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle('🎯 设定今日目标')
            dialog.setFixedSize(400, 220)
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 16, 20, 16)
            layout.setSpacing(10)

            layout.addWidget(QLabel('今天主要学什么？'))
            goal_input = QLineEdit()
            goal_input.setPlaceholderText('例如：数学导数+英语阅读')
            layout.addWidget(goal_input)

            rounds_layout = QHBoxLayout()
            rounds_layout.addWidget(QLabel('预计几轮：'))
            rounds_spin = QSpinBox()
            rounds_spin.setRange(1, 10)
            rounds_spin.setValue(4)
            rounds_spin.setFixedWidth(60)
            rounds_layout.addWidget(rounds_spin)
            rounds_layout.addStretch()
            layout.addLayout(rounds_layout)

            btn_layout = QHBoxLayout()
            submit_btn = QPushButton('开始')
            skip_btn = QPushButton('跳过')
            submit_btn.clicked.connect(dialog.accept)
            skip_btn.clicked.connect(dialog.reject)
            btn_layout.addWidget(skip_btn)
            btn_layout.addWidget(submit_btn)
            layout.addLayout(btn_layout)

            if dialog.exec_():
                self.goal_text = goal_input.text().strip()
                planned = rounds_spin.value()
                goal_store.save({'date': datetime.now().date().isoformat(), 'goal': self.goal_text, 'planned_rounds': planned})
                # 写入 daily_log 的 daily_goal 字段
                daily_data = LocalSync._load()
                daily_data['daily_goal'] = {
                    'description': self.goal_text,
                    'planned_rounds': planned
                }
                LocalSync._save()
                self.update_study_display()
                log.info(f'[目标] 设定: {self.goal_text} ({planned}轮)')
        except Exception as e:
            log.error(f'[目标] 对话框异常: {e}')

    def _prompt_round_goal(self):
        """休息结束后弹出本轮目标：学科6选1 + 目标文本 + 1分钟倒计时自动提交，金色选中态"""
        try:
            saved = [False]
            dialog = QDialog(self)
            dialog.setWindowTitle('🎯 本轮目标')
            dialog.setFixedSize(480, 300)
            dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
            layout = QVBoxLayout(dialog)
            layout.setContentsMargins(20, 16, 20, 16)
            layout.setSpacing(12)

            layout.addWidget(QLabel(f'第{self._round_count + 1}轮：这轮学什么？'))

            # 学科按钮（大按钮，金色选中态）
            layout.addWidget(QLabel('📚 学科：'))
            subject_layout = QHBoxLayout()
            subject_layout.setSpacing(6)
            subject_btns = []
            subject_val = ['未选']
            for subj in _SUBJECTS:
                btn = QPushButton(subj)
                btn.setCheckable(True)
                btn.setFixedSize(56, 36)
                btn.setStyleSheet("""
                    QPushButton { background: #1e1e26; color: #b8b4ac; border: 1px solid #252530; border-radius: 8px; font-size: 12px; }
                    QPushButton:checked { background: #d4a853; color: #0d0d12; border: none; font-weight: bold; }
                    QPushButton:hover:!checked { background: #2a2a35; }
                """)
                subject_btns.append(btn)
                subject_layout.addWidget(btn)
                def _make_handler(s, sv, b):
                    def handler(checked):
                        if checked:
                            sv[0] = s
                            for bb in subject_btns:
                                if bb is not b:
                                    bb.blockSignals(True)
                                    bb.setChecked(False)
                                    bb.blockSignals(False)
                        else:
                            if sv[0] == s:
                                sv[0] = '未选'
                    return handler
                btn.clicked.connect(_make_handler(subj, subject_val, btn))
            layout.addLayout(subject_layout)

            # 目标文本
            goal_input = QLineEdit()
            goal_input.setPlaceholderText('可选：这轮的具体内容')
            layout.addWidget(goal_input)

            # 信息栏 + 倒计时
            info_bar = QWidget()
            info_bar.setStyleSheet('background: #16161c; border-radius: 6px;')
            info_layout = QHBoxLayout(info_bar)
            info_layout.setContentsMargins(10, 6, 10, 6)
            info_lbl = QLabel(f'⏳ {AUTO_SUBMIT_SECONDS}秒后自动提交')
            info_lbl.setStyleSheet('color: #666; font-size: 11px; background: transparent;')
            info_layout.addWidget(info_lbl)
            layout.addWidget(info_bar)

            # 提交按钮
            submit_btn = QPushButton('提交')
            submit_btn.clicked.connect(dialog.accept)
            layout.addWidget(submit_btn)

            def _do_save():
                if not saved[0]:
                    saved[0] = True
                    subject = subject_val[0]
                    round_goal = goal_input.text().strip()
                    self._save_round_goal(subject, round_goal)
                    self.tray_icon.showMessage(
                        '🎯 本轮目标',
                        f'{subject} | {round_goal or "无"}',
                        QSystemTrayIcon.Information,
                        2000
                    )

            dialog.accepted.connect(_do_save)

            # 倒计时自动提交
            remaining = [AUTO_SUBMIT_SECONDS]
            def _countdown():
                remaining[0] -= 1
                if remaining[0] > 0:
                    info_lbl.setText(f'⏳ {remaining[0]}秒后自动提交')
                    QTimer.singleShot(1000, _countdown)
                else:
                    info_lbl.setText('⏳ 自动提交中...')
                    dialog.accept()
            QTimer.singleShot(1000, _countdown)

            dialog.exec_()
        except Exception as e:
            log.error(f'[轮次目标] 弹窗异常: {e}')

    def _save_round_goal(self, subject, round_goal):
        """将本轮目标写入复盘记录（更新最后一条，不创建垃圾数据）。"""
        try:
            data = review_store.load()
            today = datetime.now().date().isoformat()
            if today in data and data[today]:
                entry = data[today][-1]
                entry['round_goal'] = round_goal
                if 'subject' not in entry or entry.get('subject') == '未记录':
                    entry['subject'] = subject
                if 'label' not in entry or entry.get('label') == '未记录':
                    entry['label'] = '未记录'
                review_store.save(data)
            log.info(f'[轮次目标] 已记录: {subject} | {round_goal}')
        except Exception as e:
            log.error(f'[轮次目标] 保存失败: {e}')

    def _set_reminder_mode(self, mode):
        """设置提醒方式"""
        self.app_settings['reminder_mode'] = mode
        LocalSync.save_settings(self.app_settings)
        mode_names = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '只弹通知', 'none': '无操作'}
        self.tray_icon.showMessage('提醒方式', f'已切换为：{mode_names.get(mode, mode)}', QSystemTrayIcon.Information, 2000)
        log.info(f'[设置] 提醒方式切换为: {mode}')
        # 同步托盘卡片 UI
        self._update_tray_card()

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

        # 恢复休息结束时间（仅限今天）
        if self._rest_end_time is None and state.get('rest_end_time'):
            try:
                ret = datetime.fromisoformat(state['rest_end_time'])
                if ret.date() == datetime.now().date():
                    self._rest_end_time = ret
            except Exception as e:
                log.warning(f'[恢复] rest_end_time 解析失败: {e}')

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
            'rest_end_time': self._rest_end_time.isoformat() if self._rest_end_time else None,
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
            return

        # 如果 streak 被清零但历史数据显示昨天达标，自动恢复
        if streak['current_streak'] == 0 and streak.get('best_streak', 0) > 0:
            yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
            hist = history_store.load()
            y_data = hist.get(yesterday, {})
            y_study = y_data.get('study', 0) if isinstance(y_data, dict) else 0
            if y_study >= STREAK_THRESHOLD_HOURS:
                streak['last_streak_date'] = yesterday
                log.info(f'[打卡] 从历史恢复：昨日{y_study}h >= {STREAK_THRESHOLD_HOURS}h')

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

    def export_weekly_data(self):
        """导出最近7天数据到剪贴板"""
        history = LocalSync.load_weekly_stats()
        today = datetime.now().date()
        lines = ['日期        | 学习(h) | 休息(min)']
        lines.append('-' * 34)
        total_study = 0
        total_break = 0
        for i in range(6, -1, -1):
            d = (today - timedelta(days=i)).isoformat()
            label = (today - timedelta(days=i)).strftime('%m/%d (%a)')
            data = history.get(d, {'study': 0, 'break_minutes': 0})
            study = data.get('study', 0)
            brk = data.get('break_minutes', 0)
            total_study += study
            total_break += brk
            lines.append(f'{label}  |  {study:>5.1f}  |  {brk:>6.1f}')
        lines.append('-' * 34)
        lines.append(f'合计        |  {total_study:>5.1f}  |  {total_break:>6.1f}')
        text = '\n'.join(lines)
        QApplication.clipboard().setText(text)
        self.tray_icon.showMessage('📋 已复制到剪贴板', f'最近7天数据已导出\n\n{text}', QSystemTrayIcon.Information, 5000)
        log.info(f'[导出] 本周数据已复制到剪贴板')

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
        super().hideEvent(event)

    def closeEvent(self, event):
        try:
            event.ignore()
            self._save_active_state()
            if self.app_settings.get('close_to_tray', True):
                self.hide()
            else:
                self.quit_app()
        except Exception as e:
            log.error(f'[closeEvent 异常] {type(e).__name__}: {e}')

    def quit_app(self):
        try:
            self._save_active_state()
            self.tray_icon.hide()
            if hasattr(self, 'floating_ball'):
                self.floating_ball.hide()
            if hasattr(self, 'countdown_overlay'):
                self.countdown_overlay.hide_overlay()
            self.timer.stop()
            QApplication.quit()
        except Exception as e:
            log.error(f'[quit_app 异常] {type(e).__name__}: {e}')


_single_instance = SingleInstanceChecker()


def main():
    if _single_instance.is_already_running():
        log.warning('休息提醒程序已经在运行中！')
        if '--silent' not in sys.argv:
            a = QApplication([])
            QMessageBox.warning(None, '已在运行', '程序已在运行中！\n请检查系统托盘图标。')
        sys.exit(0)

    # 全局异常处理器
    def excepthook(exc_type, exc_value, exc_tb):
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
    sys.excepthook = excepthook

    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        log.error("[DPIAware] 设置失败")

    app = QApplication([])
    app.setQuitOnLastWindowClosed(False)

    silent = '--silent' in sys.argv
    widget = RestReminderWidget(silent_start=silent)
    if silent:
        widget.hide()
    else:
        widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
