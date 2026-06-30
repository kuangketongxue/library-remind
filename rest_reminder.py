"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
- 20-20-20 护眼提醒：每 20 分钟浮窗提示看远处 20 秒
- 监控电池充电状态
- 学习时长本地计数（每次倒计时完成算 1 小时）
- 数据本地持久化（.daily_log.json）
"""
import sys
import os
# Python 版本守卫：vendor 内 .pyd 按 CPython ABI 编译，跨次版本不兼容
# 启动用 python 指向 3.10 而 vendor 为 3.14 编译时会出现 ImportError: cannot import name 'sip'
if not getattr(sys, 'frozen', False) and sys.version_info[:2] != (3, 14):
    print(f"[rest_reminder] 需要 Python 3.14（当前 {sys.version_info.major}.{sys.version_info.minor}）。"
          f"\n请用: C:\\Python314\\python.exe rest_reminder.py --silent", file=sys.stderr)
    sys.exit(2)
# vendor 目录：开箱即用，无需 pip install -r requirements.txt
# PyInstaller 打包后 (sys.frozen=True) 由 spec 处理依赖，跳过
_VENDOR_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor')
if not getattr(sys, 'frozen', False) and os.path.isdir(_VENDOR_DIR) and _VENDOR_DIR not in sys.path:
    sys.path.insert(0, _VENDOR_DIR)
    # Qt 插件目录：让 Qt 找到 platforms/qwindows.dll、imageformats、styles 等
    # 不设会报 "no Qt platform plugin could be initialized"
    # 同时设 QT_PLUGIN_PATH（标准入口）和 QT_QPA_PLATFORM_PLUGIN_PATH（platforms 直查）
    _QT_PLUGINS = os.path.join(_VENDOR_DIR, 'PyQt5', 'Qt5', 'plugins')
    if os.path.isdir(_QT_PLUGINS):
        os.environ.setdefault('QT_PLUGIN_PATH', _QT_PLUGINS)
        os.environ.setdefault('QT_QPA_PLATFORM_PLUGIN_PATH', os.path.join(_QT_PLUGINS, 'platforms'))
import time
import random
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
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox, QFrame, QTabWidget, QStackedWidget, QComboBox, QLineEdit, QScrollArea, QDialog, QSlider, QSpinBox, QGroupBox, QTextBrowser, QToolTip, QGridLayout)
from PyQt5.QtCore import QTimer, Qt, QPoint, QPointF, QEvent, QThread, pyqtSignal, QRect
from PyQt5.QtGui import (QIcon, QFont, QPainter, QColor, QBrush, QPen,
                         QLinearGradient, QRadialGradient, QPainterPath, QPixmap)
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from tray_card import TrayCardWidget
from feishu_calendar import FeishuCalendarManager
import psutil
import wave
import struct
import math
import subprocess
import tempfile
import atexit
import winreg
import traceback
import base64
import hashlib
import backup


# ═══ API Key 加密工具 ═══
_KEY_PREFIX = 'enc:'  # 区分加密 key 和明文 key

def _get_machine_salt():
    """基于机器信息生成固定盐值（不依赖额外库）"""
    import socket
    raw = f'{socket.gethostname()}|{os.getlogin()}|RestReminder'
    return hashlib.sha256(raw.encode()).digest()[:16]

def _encrypt_key(plaintext):
    """XOR + base64 加密 API Key"""
    if not plaintext or plaintext.startswith(_KEY_PREFIX):
        return plaintext
    salt = _get_machine_salt()
    xored = bytes(b ^ salt[i % len(salt)] for i, b in enumerate(plaintext.encode('utf-8')))
    return _KEY_PREFIX + base64.b64encode(xored).decode('ascii')

def _decrypt_key(stored):
    """解密 API Key，兼容旧版明文"""
    if not stored:
        return stored
    if not stored.startswith(_KEY_PREFIX):
        return stored  # 旧版明文，直接返回
    try:
        salt = _get_machine_salt()
        xored = base64.b64decode(stored[len(_KEY_PREFIX):])
        return bytes(b ^ salt[i % len(salt)] for i, b in enumerate(xored)).decode('utf-8')
    except Exception:
        return stored  # 解密失败，返回原值
import winsound
import logging
from logging.handlers import RotatingFileHandler
from storage import JSONStore

# 子目录模块需显式加入 sys.path
_PRO_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest-reminder-site')
if os.path.isdir(_PRO_DIR) and _PRO_DIR not in sys.path:
    sys.path.insert(0, _PRO_DIR)

# 日志配置：写入文件（pythonw 模式下 print 全部丢失），自动轮转 3×1MB
VERSION = 'v6.1.0'
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
achievements_store = JSONStore('.achievements.json',   default={'earned': {}}, ensure_ascii=False)

# ═══ 成就定义 ═══
_ACHIEVEMENTS = [
    # 学习时长里程碑
    {'id': 'first_hour',    'name': '初出茅庐',   'desc': '累计学习 1 小时',        'icon': '📖', 'category': 'study',
     'check': lambda d: d.get('total_study', 0) >= 1},
    {'id': 'ten_hours',     'name': '学海无涯',   'desc': '累计学习 10 小时',       'icon': '📚', 'category': 'study',
     'check': lambda d: d.get('total_study', 0) >= 10},
    {'id': 'fifty_hours',   'name': '废寝忘食',   'desc': '累计学习 50 小时',       'icon': '🔥', 'category': 'study',
     'check': lambda d: d.get('total_study', 0) >= 50},
    {'id': 'hundred_hours', 'name': '博学多才',   'desc': '累计学习 100 小时',      'icon': '🎓', 'category': 'study',
     'check': lambda d: d.get('total_study', 0) >= 100},
    {'id': 'week_30h',      'name': '一周巅峰',   'desc': '单周学习 30 小时',       'icon': '⚡', 'category': 'study',
     'check': lambda d: d.get('week_study', 0) >= 30},
    {'id': 'month_100h',    'name': '月度学霸',   'desc': '单月学习 100 小时',      'icon': '🌙', 'category': 'study',
     'check': lambda d: d.get('month_study', 0) >= 100},
    # 连续打卡
    {'id': 'streak_3',      'name': '三天打鱼',   'desc': '连续打卡 3 天',          'icon': '🌱', 'category': 'streak',
     'check': lambda d: d.get('current_streak', 0) >= 3},
    {'id': 'streak_7',      'name': '一周坚持',   'desc': '连续打卡 7 天',          'icon': '🌿', 'category': 'streak',
     'check': lambda d: d.get('current_streak', 0) >= 7},
    {'id': 'streak_14',     'name': '两周达人',   'desc': '连续打卡 14 天',         'icon': '🌳', 'category': 'streak',
     'check': lambda d: d.get('current_streak', 0) >= 14},
    {'id': 'streak_30',     'name': '月度之星',   'desc': '连续打卡 30 天',         'icon': '⭐', 'category': 'streak',
     'check': lambda d: d.get('current_streak', 0) >= 30},
    # 单日成就
    {'id': 'daily_4h',      'name': '半日充实',   'desc': '单日学习 4 小时',        'icon': '💪', 'category': 'daily',
     'check': lambda d: d.get('today_study', 0) >= 4},
    {'id': 'daily_8h',      'name': '全天奋战',   'desc': '单日学习 8 小时',        'icon': '🏆', 'category': 'daily',
     'check': lambda d: d.get('today_study', 0) >= 8},
    # 复盘质量
    {'id': 'review_10',     'name': '反思达人',   'desc': '累计完成 10 次复盘',     'icon': '📝', 'category': 'review',
     'check': lambda d: d.get('total_reviews', 0) >= 10},
    {'id': 'review_50',     'name': '深度思考',   'desc': '累计完成 50 次复盘',     'icon': '🧠', 'category': 'review',
     'check': lambda d: d.get('total_reviews', 0) >= 50},
    {'id': 'review_100',    'name': '反思大师',   'desc': '累计完成 100 次复盘',    'icon': '🎓', 'category': 'review',
     'check': lambda d: d.get('total_reviews', 0) >= 100},
    {'id': 'perfect_score', 'name': '完美一轮',   'desc': '复盘评分达到 100 分',    'icon': '💯', 'category': 'review',
     'check': lambda d: d.get('max_score', 0) >= 100},
    # 轮次
    {'id': 'rounds_10',     'name': '初露锋芒',   'desc': '累计完成 10 轮学习',     'icon': '🎯', 'category': 'rounds',
     'check': lambda d: d.get('total_rounds', 0) >= 10},
    {'id': 'rounds_50',     'name': '持之以恒',   'desc': '累计完成 50 轮学习',     'icon': '🏅', 'category': 'rounds',
     'check': lambda d: d.get('total_rounds', 0) >= 50},
    {'id': 'rounds_100',    'name': '百日修炼',   'desc': '累计完成 100 轮学习',    'icon': '👑', 'category': 'rounds',
     'check': lambda d: d.get('total_rounds', 0) >= 100},
]

# ═══ 默认 AI 提供商（通过 Cloudflare Pages Function 代理，key 不暴露）═══
# Worker URL: https://crazy-rest-reminder.pages.dev/api/ai-proxy
# key 存在 CF Pages secrets，用户看不到
_DEFAULT_AI_PROVIDERS = [
    {
        'id': 'default_proxy',
        'name': '内置免费 AI（Cloudflare 代理）',
        'url': 'https://crazy-rest-reminder.pages.dev/api/ai-proxy',
        'model': 'auto',
        'api_key': 'public',  # Worker 不需要客户端 key，填占位符
        'enabled': True,
        'priority': 1,
        'is_default': True,
    },
]


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


def _build_time_buckets():
    """返回 12 个 2 小时时段 bucket：(label, start_hour, end_hour)

    覆盖全天 0-24 时，包含深夜/凌晨（22-24、0-2、2-4、4-6），
    适配熬夜学习场景。22-24 与 0-6 分开，让"晚睡"和"早起"区分开。
    """
    return [
        ('0-2时', 0, 2),
        ('2-4时', 2, 4),
        ('4-6时', 4, 6),
        ('6-8时', 6, 8),
        ('8-10时', 8, 10),
        ('10-12时', 10, 12),
        ('12-14时', 12, 14),
        ('14-16时', 14, 16),
        ('16-18时', 16, 18),
        ('18-20时', 18, 20),
        ('20-22时', 20, 22),
        ('22-24时', 22, 24),
    ]


def _aggregate_reviews_by_time(reviews_data, days=7):
    """按 2 小时时段聚合复盘评分，返回 {bucket_label: [scores]}"""
    from datetime import timedelta
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    buckets = {b[0]: [] for b in _build_time_buckets()}
    for d, items in sorted(reviews_data.items()):
        try:
            if datetime.fromisoformat(d).date() < start:
                continue
            entries = items if isinstance(items, list) else [items]
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                t = entry.get('time', '')
                try:
                    h = int(t.split(':')[0])
                except (ValueError, IndexError):
                    continue
                for label, s, e in _build_time_buckets():
                    if s <= h < e:
                        buckets[label].append(entry.get('score', 0))
                        break
        except (ValueError, TypeError):
            pass
    return buckets


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


# ═══ 主题系统 ═══
THEMES = {
    'dark': {
        'name': '深色',
        'bg_base': '#0d0d12',
        'bg_raised': '#18181f',
        'bg_sidebar': '#111116',
        'bg_input': '#16161c',
        'bg_card': '#18181f',
        'text_primary': '#e8e4dc',
        'text_secondary': '#888',
        'text_muted': '#555',
        'accent': '#d4a853',
        'accent_hover': '#e8bc6a',
        'accent_bg': 'rgba(212,168,83,0.12)',
        'border': '#252530',
        'border_light': 'rgba(255,255,255,0.05)',
        'scrollbar': '#2a2a35',
        'btn_bg': 'rgba(255,255,255,0.05)',
        'btn_hover': 'rgba(255,255,255,0.10)',
        'btn_text': '#b8b4ac',
        'success': '#78B450',
        'danger': '#c95454',
        'warning': '#fcc419',
        'info': '#6a8cbb',
    },
    'light': {
        'name': '浅色',
        'bg_base': '#f8f7f4',
        'bg_raised': '#ffffff',
        'bg_sidebar': '#f0efe8',
        'bg_input': '#ffffff',
        'bg_card': '#ffffff',
        'text_primary': '#1a1a1a',
        'text_secondary': '#666',
        'text_muted': '#999',
        'accent': '#b8860b',
        'accent_hover': '#d4a017',
        'accent_bg': 'rgba(184,134,11,0.08)',
        'border': '#e0ddd5',
        'border_light': 'rgba(0,0,0,0.06)',
        'scrollbar': '#ccc',
        'btn_bg': 'rgba(0,0,0,0.04)',
        'btn_hover': 'rgba(0,0,0,0.08)',
        'btn_text': '#444',
        'success': '#2e7d32',
        'danger': '#c62828',
        'warning': '#f57f17',
        'info': '#1565c0',
    },
}

def _get_system_theme():
    """检测系统主题偏好（Windows 10/11）"""
    try:
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
            r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
        value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
        winreg.CloseKey(key)
        return 'light' if value == 1 else 'dark'
    except Exception:
        return 'dark'

def _resolve_theme(theme_pref):
    """解析主题偏好（dark/light/system）"""
    if theme_pref == 'system':
        return _get_system_theme()
    return theme_pref if theme_pref in THEMES else 'dark'

def _apply_theme_stylesheet(theme_name):
    """生成全局主题 stylesheet"""
    t = THEMES.get(theme_name, THEMES['dark'])
    return f"""
        QWidget {{ background-color: {t['bg_base']}; color: {t['text_primary']}; }}
        QWidget#mainWindow {{
            background-color: {t['bg_base']};
            border: 1px solid {t['border_light']};
            border-radius: 14px;
        }}
        QLabel {{ color: {t['text_primary']}; font-size: 13px; background: transparent;
                  font-family: 'Segoe UI Emoji', 'Microsoft YaHei', sans-serif; }}
        QFrame#sidebar {{
            background: {t['bg_sidebar']};
            border-right: 1px solid {t['border']};
        }}
        QPushButton#navBtn {{
            background: transparent; color: {t['text_secondary']};
            border: none; border-radius: 8px;
            padding: 10px 14px; font-size: 13px;
            font-family: 'Microsoft YaHei', sans-serif;
            text-align: left; min-height: 44px;
        }}
        QPushButton#navBtn:hover {{ background: {t['accent_bg']}; color: {t['accent']}; }}
        QPushButton#navBtn:checked {{
            background: {t['accent_bg']}; color: {t['accent']};
        }}
        QPushButton {{
            background: {t['btn_bg']}; color: {t['btn_text']};
            border: 1px solid {t['border']};
            border-radius: 8px; padding: 8px 16px; font-size: 12px;
            font-family: 'Microsoft YaHei', sans-serif;
        }}
        QPushButton:hover {{ background: {t['btn_hover']}; color: {t['text_primary']}; }}
        QPushButton#accentBtn {{
            background: {t['accent']}; color: {t['bg_base']}; border: none;
            font-weight: bold;
        }}
        QPushButton#accentBtn:hover {{ background: {t['accent_hover']}; }}
        QPushButton#dangerBtn {{ color: {t['danger']}; border-color: rgba(201,84,84,0.20); }}
        QPushButton#dangerBtn:hover {{ background: rgba(201,84,84,0.10); }}
        QLineEdit {{ background: {t['bg_input']}; color: {t['text_primary']}; border: 1px solid {t['border']};
            border-radius: 8px; padding: 8px 12px; font-size: 12px; }}
        QComboBox {{ background: {t['bg_input']}; color: {t['text_primary']}; border: 1px solid {t['border']};
            border-radius: 8px; padding: 7px 12px; font-size: 12px; min-width: 100px; }}
        QComboBox::drop-down {{ border: none; }}
        QFrame#statCard {{
            background: {t['bg_card']}; border: 1px solid {t['border']};
            border-radius: 12px;
        }}
        QFrame#sectionCard {{
            background: {t['bg_card']}; border: 1px solid {t['border']};
            border-radius: 12px;
        }}
        QScrollBar:vertical {{ background: transparent; width: 6px; }}
        QScrollBar::handle:vertical {{ background: {t['scrollbar']}; border-radius: 3px; }}
        QScrollBar::handle:vertical:hover {{ background: {t['text_muted']}; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        QFrame#divider {{
            background: {t['border']}; max-height: 1px; min-height: 1px;
        }}
        QTextBrowser {{ background: {t['bg_card']}; color: {t['text_primary']};
            border: 1px solid {t['border']}; border-radius: 8px; padding: 12px; }}
    """


class FloatingBall(QWidget):
    """浮球（⏰ 60×60）— 点击弹出 info 浮层，右键菜单，休息时显示环形进度条"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.dragging = False
        self.drag_position = None
        self.click_time = None
        self._progress = 0.0  # 0.0~1.0 环形进度（休息倒计时用）

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

    def set_progress(self, ratio):
        """设置环形进度 0.0~1.0（1=满圈，0=空圈），触发重绘"""
        if abs(self._progress - ratio) > 0.005:
            self._progress = max(0.0, min(1.0, ratio))
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        cx, cy = 30, 30  # 中心
        radius = 26      # 环形进度半径

        # ── 休息时：环形进度条（线性渐变 琥珀→亮金） ──
        if self._progress > 0.001:
            # 背景环（暗色底）
            bg_pen = QPen(QColor(40, 40, 48), 4)
            bg_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(bg_pen)
            painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 0, 5760)

            # 进度环（渐变）
            ring_grad = QLinearGradient(cx - radius, cy - radius, cx + radius, cy + radius)
            ring_grad.setColorAt(0.0, QColor(212, 168, 83))
            ring_grad.setColorAt(1.0, QColor(240, 200, 112))
            progress_pen = QPen(QBrush(ring_grad), 4)
            progress_pen.setCapStyle(Qt.RoundCap)
            painter.setPen(progress_pen)
            span_angle = int(5760 * self._progress)
            painter.drawArc(cx - radius, cy - radius, radius * 2, radius * 2, 0, span_angle)

        # ── 内层圆（径向渐变，光源偏上模拟能量球） ──
        ball_grad = QRadialGradient(QPointF(cx, cy - 8), 34)
        ball_grad.setColorAt(0.0, QColor(42, 37, 32))
        ball_grad.setColorAt(1.0, QColor(15, 14, 18))
        painter.setBrush(QBrush(ball_grad))
        # 半透描边（柔光感）
        edge_pen = QPen(QColor(212, 168, 83, 90))
        edge_pen.setWidthF(0.8)
        painter.setPen(edge_pen)
        painter.drawEllipse(4, 4, 52, 52)

        # ── 矢量图标（取代 emoji，保证跨机器一致） ──
        mw = self.main_window
        painter.setPen(Qt.NoPen)
        if mw.timer_state == 'resting':
            # 休息态：暂停符号（两条圆角竖线，与闪电形成播放/暂停语义）
            painter.setBrush(QBrush(QColor(240, 200, 112)))
            painter.drawRoundedRect(24, 22, 5, 16, 2.5, 2.5)
            painter.drawRoundedRect(33, 22, 5, 16, 2.5, 2.5)
        else:
            # 学习态：矢量闪电（亮金渐变填充）
            bolt_path = QPainterPath()
            bolt_path.moveTo(33, 18)
            bolt_path.lineTo(22, 34)
            bolt_path.lineTo(29, 34)
            bolt_path.lineTo(27, 46)
            bolt_path.lineTo(38, 30)
            bolt_path.lineTo(31, 30)
            bolt_path.closeSubpath()
            bolt_grad = QLinearGradient(22, 18, 38, 46)
            bolt_grad.setColorAt(0.0, QColor(240, 200, 112))
            bolt_grad.setColorAt(1.0, QColor(212, 168, 83))
            painter.setBrush(QBrush(bolt_grad))
            painter.setPen(QPen(QColor(212, 168, 83), 0.5))
            painter.drawPath(bolt_path)

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
            if self.click_time is None:
                return
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
            popup._title_lbl = title_lbl
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

            # 目标 + 轮次（目标可点击：未设目标时点击进入设置）
            goal_row = QHBoxLayout()
            goal_row.setContentsMargins(0, 0, 0, 0)
            goal_row.setSpacing(4)
            popup._goal_lbl = QPushButton('')
            popup._goal_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._goal_lbl.setCursor(Qt.PointingHandCursor)
            popup._goal_lbl.setStyleSheet('''
                QPushButton {
                    background: transparent; border: none;
                    color: #d4a853; text-align: left;
                    padding: 0;
                }
                QPushButton:hover { color: #f0c060; text-decoration: underline; }
                QPushButton:pressed { color: #b8901f; }
            ''')
            popup._goal_lbl.setToolTip('点击设置今日目标')
            popup._goal_lbl.clicked.connect(self._on_goal_label_clicked)
            goal_row.addWidget(popup._goal_lbl, 1)
            popup._round_lbl = QLabel('')
            popup._round_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._round_lbl.setStyleSheet('color: #888;')
            popup._round_lbl.setAlignment(Qt.AlignRight)
            goal_row.addWidget(popup._round_lbl, 0)
            layout.addLayout(goal_row)

            # 飞书日程（一行摘要）
            popup._cal_lbl = QLabel('')
            popup._cal_lbl.setFont(QFont('Microsoft YaHei', 8))
            popup._cal_lbl.setStyleSheet('color: #6a8cbb;')
            popup._cal_lbl.setWordWrap(True)
            popup._cal_lbl.setVisible(False)
            layout.addWidget(popup._cal_lbl)

            # 开始/暂停按钮（只连接一次）
            popup._action_btn = QPushButton()
            popup._action_btn.setFixedHeight(28)
            popup._action_btn.setCursor(Qt.PointingHandCursor)
            popup._action_btn.setStyleSheet('QPushButton { background: #3b82f6; color: #fff; border: none; border-radius: 6px; font-size: 11px; font-weight: bold; } QPushButton:hover { background: #2563eb; }')
            popup._action_btn.clicked.connect(self._on_popup_btn_clicked)
            layout.addWidget(popup._action_btn)

            mw._info_popup = popup

        # ★ 应用/刷新主题样式（应对主题切换）
        self._apply_popup_theme(popup)
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


    def _apply_popup_theme(self, popup):
        """应用当前主题到 info popup（支持主题切换刷新，覆盖首次创建的硬编码默认）"""
        t = THEMES.get(self.main_window._current_theme, THEMES['dark'])
        popup.setStyleSheet(f"""
            QFrame#infoRoot {{
                background-color: {t['bg_card']};
                border: 1px solid {t['border']};
                border-radius: 12px;
            }}
            QLabel {{ background: transparent; }}
        """)
        if hasattr(popup, '_title_lbl'):
            popup._title_lbl.setStyleSheet(f'color: {t["text_muted"]};')
        popup._timer_lbl.setStyleSheet(f'color: {t["accent"]};')
        popup._study_lbl.setStyleSheet(f'color: {t["success"]};')
        popup._goal_lbl.setStyleSheet(f'''
            QPushButton {{
                background: transparent; border: none;
                color: {t["accent"]}; text-align: left;
                padding: 0;
            }}
            QPushButton:hover {{ color: {t["accent_hover"]}; text-decoration: underline; }}
            QPushButton:pressed {{ color: {t["accent"]}; }}
        ''')
        popup._round_lbl.setStyleSheet(f'color: {t["text_secondary"]};')
        popup._cal_lbl.setStyleSheet(f'color: {t["info"]};')
        popup._action_btn.setStyleSheet(
            f'QPushButton {{ background: {t["accent"]}; color: {t["bg_base"]}; border: none; border-radius: 6px; font-size: 11px; font-weight: bold; }}'
            f' QPushButton:hover {{ background: {t["accent_hover"]}; }}'
        )


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
        # 飞书日程摘要
        if hasattr(popup, '_cal_lbl'):
            cal_mgr = getattr(mw, '_calendar_mgr', None)
            cal_enabled = getattr(mw, '_calendar_enabled', False)
            if cal_mgr and cal_enabled:
                cal_text = cal_mgr.get_display_text(short=True)
                if prev.get('cal') != cal_text:
                    popup._cal_lbl.setText(cal_text)
                    popup._cal_lbl.setVisible(True)
                    prev['cal'] = cal_text
            else:
                popup._cal_lbl.setVisible(False)
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

    def _on_goal_label_clicked(self):
        """点击 popup 中的目标标签：弹出目标设置对话框，未设目标时强制弹（不跳过）"""
        mw = self.main_window
        was_empty = not mw.goal_text
        log.info(f'[goal-label] clicked, was_empty={was_empty}')
        # 临时清空 _prompt_goal 的早退条件，强制弹出
        mw._show_goal_dialog()
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
    def save_daily_stats(cls, rounds=0):
        """保存今日数据到历史记录（每次调用都更新今日数据）"""
        data = cls._load()
        today = datetime.now().date().isoformat()
        history = history_store.load()
        history[today] = {
            'study': round(data.get('study_hours', 0), 1),
            'break_minutes': round(data.get('break_minutes_today', 0), 1),
            'rounds': rounds
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


# ═══ 每周邮件报告（agently-cli） ═══
class _WeeklyReportWorker(QThread):
    """后台线程：生成并通过 agently-cli 发送每周学习报告邮件"""
    result_ready = pyqtSignal(bool, str)  # (success, message)

    def __init__(self, recipient):
        super().__init__()
        self._recipient = recipient

    def run(self):
        try:
            # 生成周报
            result = generate_report('weekly', force_refresh=True)
            if not result.get('ok'):
                data = _build_report_data('weekly')
                report_text = _local_fallback_report('weekly', data)
            else:
                report_text = result.get('content', '')

            # 构建 HTML 邮件体
            html_content = _md_to_html(report_text)
            html_body = (
                '<div style="max-width:680px;margin:0 auto;font-family:Segoe UI,Microsoft YaHei,sans-serif;color:#333;">'
                '<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);padding:24px;border-radius:12px;color:#e8e4dc;">'
                '<h2 style="margin:0;color:#d4a853;">⚡ 休息提醒 · 本周学习报告</h2>'
                '<p style="color:#888;margin:4px 0 0;">AI 智能分析 · 每周自动推送</p>'
                '</div>'
                '<div style="background:#fff;padding:24px;border-radius:0 0 12px 12px;border:1px solid #eee;">'
                + html_content +
                '</div>'
                '<p style="color:#999;font-size:12px;text-align:center;margin-top:16px;">'
                '由休息提醒自动生成 · '
                '<a href="https://crazy-rest-reminder.pages.dev" style="color:#d4a853;">了解更多</a></p>'
                '</div>'
            )

            # 写入临时 HTML 文件（必须在 cwd 下，agently-cli --body-file 只接受相对路径）
            html_dir = tempfile.gettempdir()
            html_name = 'rest_reminder_weekly.html'
            html_path = os.path.join(html_dir, html_name)
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_body)

            # 通过 agently-cli 发送（两阶段：先获取确认令牌，再确认）
            # 自动查找 agently-cli 路径（npm 全局安装可能在 PATH 外）
            import shutil
            agently_bin = shutil.which('agently-cli')
            if not agently_bin:
                npm_global = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'agently-cli.cmd')
                if os.path.isfile(npm_global):
                    agently_bin = npm_global
            if not agently_bin:
                self.result_ready.emit(False, 'agently-cli 未安装（npm install -g @tencent-qqmail/agently-cli）')
                return

            cmd_base = [agently_bin, 'message', '+send',
                         '--to', self._recipient,
                         '--subject', 'RestReminder Weekly Report',
                         '--body-file', html_name]

            # 第一阶段：获取 confirmation token（cwd 必须在 html 文件所在目录）
            result1 = subprocess.run(cmd_base, capture_output=True, text=True, timeout=60, cwd=html_dir)
            if result1.returncode != 0:
                err = (result1.stderr or result1.stdout)[:200]
                self.result_ready.emit(False, f'agently-cli 错误: {err}')
                return

            # 解析确认令牌
            import json
            try:
                output = json.loads(result1.stdout.strip())
                ctk = output.get('data', {}).get('confirmation_token', '')
            except (json.JSONDecodeError, AttributeError):
                self.result_ready.emit(False, '无法解析 agently-cli 响应')
                return

            if not ctk:
                self.result_ready.emit(False, '未获取到确认令牌')
                return

            # 第二阶段：确认发送
            cmd_confirm = cmd_base + ['--confirmation-token', ctk]
            result2 = subprocess.run(cmd_confirm, capture_output=True, text=True, timeout=60, cwd=html_dir)
            if result2.returncode != 0:
                err = (result2.stderr or result2.stdout)[:200]
                self.result_ready.emit(False, f'发送失败: {err}')
                return

            self.result_ready.emit(True, '邮件发送成功')
            log.info('[周报] 邮件通过 agently-cli 发送成功')
        except subprocess.TimeoutExpired:
            self.result_ready.emit(False, 'agently-cli 超时（60秒）')
        except FileNotFoundError:
            self.result_ready.emit(False, 'agently-cli 未安装（npm install -g @tencent-qqmail/agently-cli）')
        except Exception as e:
            self.result_ready.emit(False, str(e))
            log.warning(f'[周报] 发送失败: {e}')


# ═══ 环境白噪音 ═══
_AMBIENT_SOUNDS = {
    'rain': ('\u96e8\u58f0', 44100, 3),
    'forest': ('\u68ee\u6797', 44100, 3),
    'cafe': ('\u5496\u5561\u5385', 44100, 3),
    'white': ('\u767d\u566a\u97f3', 44100, 3),
    'brown': ('\u68d5\u566a\u97f3', 44100, 3),
}

def _generate_ambient_wav(sound_type, duration=30, sample_rate=44100):
    """生成高质量环境音 WAV（Voss-McCartney粉红噪声 + 立体声 + dithering）"""
    import random as _rng
    n_samples = sample_rate * duration
    fade_samples = int(sample_rate * 0.5)

    def _voss_pink(n, state):
        dice = state['dice']
        out = []
        for _ in range(n):
            k = 0
            while k < len(dice) - 1 and _rng.random() < 0.5:
                k += 1
            dice[k] = _rng.uniform(-1, 1)
            out.append(sum(dice))
        max_val = max(abs(v) for v in out) or 1.0
        return [v * (8.0 / max_val) for v in out]

    def _brown(n, state):
        v1, v2 = state['v1'], state['v2']
        out = []
        for _ in range(n):
            white = _rng.uniform(-1, 1)
            v1 = (v1 + white * 0.02) * 0.996
            v2 = (v2 + v1 * 0.02) * 0.996
            out.append(v2)
        state['v1'], state['v2'] = v1, v2
        max_val = max(abs(v) for v in out) or 1.0
        return [v / max_val for v in out]

    def _lowpass(data, alpha=0.1):
        out, y = [], 0.0
        for x in data:
            y += alpha * (x - y)
            out.append(y)
        return out

    def _white(n):
        return [_rng.uniform(-1, 1) for _ in range(n)]

    # 左右声道用不同随机状态（立体声）
    if sound_type == 'white':
        left = _lowpass(_white(n_samples), 0.3)
        right = _lowpass(_white(n_samples), 0.3)
    elif sound_type == 'brown':
        left = _brown(n_samples, {'v1': 0.0, 'v2': 0.0})
        right = _brown(n_samples, {'v1': 0.0, 'v2': 0.0})
    elif sound_type == 'rain':
        left_base = _voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]})
        right_base = _voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]})
        rumble_l = _lowpass(_brown(n_samples, {'v1': 0.0, 'v2': 0.0}), 0.02)
        rumble_r = _lowpass(_brown(n_samples, {'v1': 0.0, 'v2': 0.0}), 0.02)
        left = [b * 0.7 + r * 0.3 for b, r in zip(left_base, rumble_l)]
        right = [b * 0.7 + r * 0.3 for b, r in zip(right_base, rumble_r)]
    elif sound_type == 'forest':
        left = _lowpass(_voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]}), 0.05)
        right = _lowpass(_voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]}), 0.05)
        i = 0
        while i < n_samples:
            if _rng.random() < 0.0003:
                chirp_len = _rng.randint(800, 2500)
                freq = _rng.uniform(2000, 5000)
                fmod = _rng.uniform(50, 200)
                for j in range(min(chirp_len, n_samples - i)):
                    t = j / sample_rate
                    env = math.sin(math.pi * j / chirp_len)
                    bird = math.sin(2 * math.pi * (freq + fmod * math.sin(2 * math.pi * 8 * t)) * t) * env * 0.3
                    left[i + j] += bird
                    right[i + j] += bird * _rng.uniform(0.7, 1.0)
                i += chirp_len
            else:
                i += 1
    elif sound_type == 'cafe':
        left = _voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]})
        right = _voss_pink(n_samples, {'dice': [_rng.uniform(-1, 1) for _ in range(16)]})
        hum_freq = _rng.uniform(80, 150)
        for i in range(n_samples):
            hum = math.sin(2 * math.pi * hum_freq * i / sample_rate) * 0.15
            left[i] = left[i] * 0.6 + hum
            right[i] = right[i] * 0.6 + hum
        i = 0
        while i < n_samples:
            if _rng.random() < 0.001:
                clink_len = _rng.randint(300, 800)
                freq = _rng.uniform(3000, 8000)
                for j in range(min(clink_len, n_samples - i)):
                    env = math.exp(-j / (clink_len * 0.3))
                    clink = math.sin(2 * math.pi * freq * j / sample_rate) * env * 0.4
                    left[i + j] += clink
                    right[i + j] += clink * _rng.uniform(0.5, 1.0)
                i += clink_len
            else:
                i += 1
    else:
        left = [0.0] * n_samples
        right = [0.0] * n_samples

    # 归一化
    max_val = max(max(abs(v) for v in left), max(abs(v) for v in right), 0.001)
    scale = 0.85 / max_val
    left = [v * scale for v in left]
    right = [v * scale for v in right]

    # crossfade
    for i in range(min(fade_samples, n_samples)):
        factor = i / fade_samples
        left[i] *= factor
        right[i] *= factor
        left[n_samples - 1 - i] *= factor
        right[n_samples - 1 - i] *= factor

    # 写入立体声 WAV + dithering
    cache_dir = os.path.join(tempfile.gettempdir(), 'rest_reminder_ambient')
    os.makedirs(cache_dir, exist_ok=True)
    wav_path = os.path.join(cache_dir, f'{sound_type}.wav')
    # 立体声文件大小 = header + 2ch × 2bytes × samples
    expected_size = 44 + n_samples * 4
    if os.path.exists(wav_path) and os.path.getsize(wav_path) >= expected_size * 0.9:
        return wav_path

    with wave.open(wav_path, 'w') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        CHUNK = 32768
        for start in range(0, n_samples, CHUNK):
            end = min(start + CHUNK, n_samples)
            raw = bytearray()
            for i in range(start, end):
                # dithering 减少量化失真
                l = int((left[i] + _rng.uniform(-0.0005, 0.0005)) * 32767)
                r = int((right[i] + _rng.uniform(-0.0005, 0.0005)) * 32767)
                raw += struct.pack('<hh', max(-32768, min(32767, l)), max(-32768, min(32767, r)))
            wf.writeframes(raw)
    return wav_path


class AmbientPlayer:
    """环境音播放器（基于 QMediaPlayer）"""

    def __init__(self):
        self._player = None
        self._current_sound = None
        self._volume = 50
        self._enabled = False

    def _ensure_player(self):
        if self._player is None:
            from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
            from PyQt5.QtCore import QUrl
            self._player = QMediaPlayer()
            self._player.setVolume(self._volume)
            # 循环播放
            self._player.mediaStatusChanged.connect(self._on_media_status)
            self._QMediaContent = QMediaContent
            self._QUrl = QUrl

    def _on_media_status(self, status):
        """媒体结束时重新播放（循环）"""
        from PyQt5.QtMultimedia import QMediaPlayer
        if status == QMediaPlayer.EndOfMedia and self._enabled:
            self._player.setPosition(0)
            self._player.play()

    def play(self, sound_type):
        """播放指定环境音"""
        self._ensure_player()
        if self._current_sound == sound_type and self._player.state() == 1:
            return  # 已在播放
        self._current_sound = sound_type
        self._enabled = True
        wav_path = _generate_ambient_wav(sound_type)
        self._player.setMedia(self._QMediaContent(self._QUrl.fromLocalFile(wav_path)))
        self._player.play()
        log.info(f'[白噪音] 播放: {sound_type}')

    def stop(self):
        """停止播放"""
        self._enabled = False
        if self._player:
            self._player.stop()
        self._current_sound = None

    def set_volume(self, vol):
        """设置音量 0-100"""
        self._volume = max(0, min(100, vol))
        if self._player:
            self._player.setVolume(self._volume)

    @property
    def is_playing(self):
        if self._player:
            return self._player.state() == 1
        return False


class SingleInstanceChecker:
    """单实例检查器 — Windows Named Mutex + 文件锁双保险
    
    优先使用 Windows Named Mutex（内核级，进程崩溃自动释放，无竞态）。
    文件锁作为降级方案（非 Windows 平台或 Mutex 创建失败时）。
    """
    _MUTEX_NAME = r'Global\RestReminder_SingleInstance_Mutex'

    def __init__(self):
        self._mutex_handle = None
        self._lock_handle = None
        self._lock_path = os.path.join(tempfile.gettempdir(), 'rest_reminder.lock')

    def is_already_running(self):
        # ── 方案 1：Windows Named Mutex（首选） ──
        try:
            kernel32 = ctypes.windll.kernel32
            # CreateMutexW: 如果 mutex 已存在，GetLastError 返回 ERROR_ALREADY_EXISTS (183)
            self._mutex_handle = kernel32.CreateMutexW(None, False, self._MUTEX_NAME)
            last_error = kernel32.GetLastError()
            if last_error == 183:  # ERROR_ALREADY_EXISTS
                if self._mutex_handle:
                    kernel32.CloseHandle(self._mutex_handle)
                    self._mutex_handle = None
                log.info('[单实例] Named Mutex 已存在，另一个实例正在运行')
                return True
            elif self._mutex_handle:
                log.info('[单实例] Named Mutex 创建成功，本实例获锁')
                atexit.register(self._cleanup_mutex)
                return False
            else:
                log.warning(f'[单实例] CreateMutexW 返回空句柄，last_error={last_error}')
        except Exception as e:
            log.warning(f'[单实例] Named Mutex 不可用: {e}')

        # ── 方案 2：文件锁降级 ──
        return self._file_lock_check()

    def _file_lock_check(self):
        """文件锁降级方案"""
        try:
            # 尝试直接获取锁
            self._lock_handle = open(self._lock_path, 'w')
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
            self._lock_handle.write(str(os.getpid()))
            self._lock_handle.flush()
            atexit.register(self._cleanup_file)
            log.info('[单实例] 文件锁获取成功')
            return False
        except IOError:
            if self._lock_handle:
                self._lock_handle.close()
                self._lock_handle = None

        # 锁被占用 → 验证旧进程是否存活
        if os.path.exists(self._lock_path):
            try:
                with open(self._lock_path, "r") as f:
                    old_pid = int(f.read().strip())
                if psutil.pid_exists(old_pid):
                    try:
                        proc = psutil.Process(old_pid)
                        cmdline = " ".join(proc.cmdline()).lower()
                        if "rest_reminder" in cmdline or "python" in cmdline:
                            log.info(f'[单实例] PID {old_pid} 仍在运行')
                            return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
            except (ValueError, IOError):
                pass
            # 旧进程已死，清理 stale lock
            try:
                os.remove(self._lock_path)
            except Exception:
                pass

        # 重新尝试获取锁
        try:
            self._lock_handle = open(self._lock_path, 'w')
            msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
            self._lock_handle.write(str(os.getpid()))
            self._lock_handle.flush()
            atexit.register(self._cleanup_file)
            log.info('[单实例] 文件锁重新获取成功')
            return False
        except Exception as e:
            # 兜底：获取失败时阻止启动（宁可误拦，不允许多实例）
            log.warning(f'[单实例] 文件锁获取失败，阻止启动: {e}')
            return True

    def _cleanup_mutex(self):
        """清理 Named Mutex"""
        try:
            if self._mutex_handle:
                kernel32 = ctypes.windll.kernel32
                kernel32.ReleaseMutex(self._mutex_handle)
                kernel32.CloseHandle(self._mutex_handle)
                self._mutex_handle = None
                log.info('[单实例] Named Mutex 已释放')
        except Exception as e:
            log.warning(f'[单实例] Mutex 清理失败: {e}')

    def _cleanup_file(self):
        """清理文件锁"""
        try:
            if self._lock_handle:
                try:
                    msvcrt.locking(self._lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except Exception:
                    pass
                self._lock_handle.close()
                self._lock_handle = None
            if os.path.exists(self._lock_path):
                os.remove(self._lock_path)
        except Exception as e:
            log.warning(f'[单实例] 文件锁清理失败: {e}')


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
            mw = getattr(self, 'main_window', None)
            sound_enabled = mw.app_settings.get('sound_enabled', True) if mw else True
            if sound_enabled:
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

        # 跳过按钮
        skip_btn = QPushButton('跳过')
        skip_btn.setFixedSize(60, 24)
        skip_btn.setCursor(Qt.PointingHandCursor)
        skip_btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.1); color: #aaa; border: 1px solid rgba(255,255,255,0.15); border-radius: 6px; font-size: 11px; } QPushButton:hover { background: rgba(255,255,255,0.2); color: #fff; }')
        skip_btn.clicked.connect(self.hide_overlay)
        skip_layout = QHBoxLayout()
        skip_layout.addStretch()
        skip_layout.addWidget(skip_btn)
        layout.addLayout(skip_layout)

        self._install_drag_on_children(self.icon_label, self.hint_label, self.countdown_label, skip_btn)

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
        self._cached_history = LocalSync.load_weekly_stats()

    def showEvent(self, event):
        super().showEvent(event)
        self._cached_history = LocalSync.load_weekly_stats()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # 标题
        painter.setPen(QColor('#faf9f5'))
        painter.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        painter.drawText(20, 25, '📊 最近7天学习统计')

        # 获取数据
        history = self._cached_history
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
            layout.addWidget(QLabel('今天还没有复盘记录，学习一轮后会自动弹出'))
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
            fill.setFixedWidth(_score_bar_width(score, is_old=info['is_old']))
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
            layout.addWidget(QLabel('暂无复盘数据，每学习 1 小时复盘一次就能看到时段分析了'))
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
        reviews = review_store.load()
        for d_str, entries in reviews.items():
            try:
                dt = datetime.strptime(d_str, '%Y-%m-%d')
                dow = dt.weekday()
                for entry in (entries if isinstance(entries, list) else [entries]):
                    if isinstance(entry, dict) and 'time' in entry:
                        try:
                            h = int(entry['time'].split(':')[0])
                            hm_data[dow][h] += 1
                        except (ValueError, IndexError):
                            pass
            except Exception:
                continue
        day_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self._draw_heatmap(layout, hm_data, [f'{h}h' for h in range(24)], day_names, '一周复盘热力图（时段×星期）')

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

        chart._bar_rects = []
        def _safe_paint_chart(e):
            p = QPainter(chart)
            try:
                paint_chart(p, chart)
            finally:
                p.end()
        chart.paintEvent = _safe_paint_chart

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

            # Y 轴标签（星期）
            for y, lbl in enumerate(y_labels):
                p.setPen(QColor('#666'))
                p.setFont(QFont('Consolas', 7))
                p.drawText(2, y * cell_size + 17, lbl)
            p.end()

        hm.paintEvent = paint_hm
        cl.addWidget(hm, 0, Qt.AlignLeft)
        layout.addWidget(card)

        # 总计
        total_study = sum(v for row in data for v in row)
        non_zero_days = sum(1 for row in data if any(v > 0 for v in row))
        avg_study = round(total_study / max(non_zero_days, 1), 1)
        summary = QLabel(f'总计: {total_study} 条复盘记录  |  活跃 {non_zero_days} 天')
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
        'review_records': review_records,  # 复盘明细
    }


def _init_ai_providers():
    """初始化 AI 提供商：首次启动填入内置默认（开箱即用），已有配置则跳过。
    幂等：已初始化过则跳过。"""
    try:
        providers = settings_store.get('ai_providers', [])
        if providers:  # 已有配置，跳过
            return
        # 首次启动：填入内置默认 providers
        settings_store.set('ai_providers', _DEFAULT_AI_PROVIDERS)
        log.info(f'[AI] 初始化 {len(_DEFAULT_AI_PROVIDERS)} 个内置免费 AI 提供商')
    except Exception as e:
        log.warning(f'[AI] 初始化默认 providers 失败（不阻塞）: {e}')


def _call_ai(prompt, model=None):
    """调用 AI API（按 ai_providers 配置遍历，OpenAI 兼容格式）"""

    _init_ai_providers()  # 启动时初始化（幂等）

    try:
        providers = settings_store.get('ai_providers', [])
    except Exception:
        providers = []

    # 按 priority 排序，只取 enabled 且有 api_key 的
    active = [p for p in providers if p.get('enabled') and p.get('api_key') and p.get('url')]
    active.sort(key=lambda p: p.get('priority', 999))

    if not active:
        return {'ok': False, 'error': '未配置任何 AI 提供商。请在「设置 → AI 服务」添加。', 'errors': []}

    headers_base = {'Content-Type': 'application/json'}

    errors = []
    for p in active:
        try:
            name = p.get('name', '未命名')
            url = p['url']
            model_id = model or p.get('model') or 'gpt-3.5-turbo'
            raw_key = p.get('api_key', '')
            api_key = _decrypt_key(raw_key) if raw_key else ''
            if not api_key:
                errors.append((name, 'API Key 解密失败'))
                continue

            body = {
                'model': model_id,
                'messages': [
                    {'role': 'system', 'content': '你是专业的学习分析顾问。根据用户的学习复盘数据，生成深度、具体、有洞察力的分析报告。用中文回答。'},
                    {'role': 'user', 'content': prompt},
                ],
                'max_tokens': 4096,
                'temperature': 0.7,
            }
            headers = {**headers_base, 'Authorization': f'Bearer {api_key}'}
            resp = requests.post(url, json=body, headers=headers, timeout=30)

            if resp.status_code == 200:
                data = resp.json()
                msg = data.get('choices', [{}])[0].get('message', {})
                content = msg.get('content', '').strip()
                # 推理模型可能把 token 全用在 reasoning 上
                if not content and msg.get('reasoning'):
                    content = msg['reasoning'].strip()
                if content:
                    return {'ok': True, 'content': content, 'provider': name}
                errors.append((name, '返回内容为空'))
            else:
                try:
                    err_body = resp.json()
                    err_msg = err_body.get('error', {}).get('message', '') or err_body.get('message', '') or resp.text[:200]
                except Exception:
                    err_msg = resp.text[:200]
                errors.append((name, f'HTTP {resp.status_code}: {err_msg}'))
        except (requests.exceptions.RequestException, ValueError, json.JSONDecodeError) as e:
            errors.append((name, str(e)))

    detail = ' | '.join(f'{n}: {m}' for n, m in errors)
    return {'ok': False, 'error': f'所有 AI 服务不可用。{detail}', 'errors': errors}


def _test_ai_provider(url, model, api_key):
    """测试单个 AI 提供商连接。返回 (success: bool, message: str)。"""
    if not url or not model or not api_key:
        return False, '请填写完整：URL、模型 ID、API Key'
    body = {
        'model': model,
        'messages': [{'role': 'user', 'content': '回复"OK"两个字'}],
        'max_tokens': 10,
    }
    try:
        headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'}
        resp = requests.post(url, json=body, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            msg = data.get('choices', [{}])[0].get('message', {})
            content = msg.get('content', '').strip()
            if not content and msg.get('reasoning'):
                content = msg['reasoning'].strip()
            return True, f'连接成功 · 返回: {content[:50]}'
        else:
            try:
                err_body = resp.json()
                err_msg = err_body.get('error', {}).get('message', '') or err_body.get('message', '') or resp.text[:100]
            except Exception:
                err_msg = resp.text[:100]
            return False, f'HTTP {resp.status_code}: {err_msg}'
    except requests.exceptions.Timeout:
        return False, '连接超时（15秒），请检查 URL 或网络'
    except requests.exceptions.ConnectionError as e:
        return False, f'连接失败: {e}'
    except Exception as e:
        return False, f'错误: {e}'




def _local_fallback_report(report_type, data):
    """AI 不可用时的本地降级报告"""
    type_names = {'daily': '日报', 'weekly': '周报', 'monthly': '月报', 'quarterly': '季报', 'yearly': '年报'}
    name = type_names.get(report_type, report_type)

    daily_lines = []
    for r in data.get('records', []):
        date = r.get('date', '?')
        study = r.get('study', 0)
        daily_lines.append(f"  - {date}：学习 {study}h")
    daily_detail = '\n'.join(daily_lines) if daily_lines else '  - 暂无记录'

    review_lines = []
    for entry in data.get('review_records', []):
        review_lines.append(
            f"  - {entry.get('time', '?')} | {entry.get('subject', '未记录')} | {entry.get('label', '')} | {entry.get('score', '?')}分"
        )
    review_detail = '\n'.join(review_lines) if review_lines else '  - 暂无复盘记录'

    tags_str = ', '.join(f'{t}({c})' for t, c in data.get('top_tags', [])) or '无'

    # 错误详情（帮助用户诊断）
    ai_error = data.get('ai_error', '')
    error_line = f'\n> ⚠️ **错误详情**：{ai_error}\n> 请在「设置 → AI 服务」检查 API Key 配置\n' if ai_error else ''

    lines = [
        f'## {name}（数据摘要）',
        f'**时间范围**：{data["date_range"]}',
        f'**学习时长**：**{data["total_study_hours"]} 小时**',
        f'**完成轮次**：**{data["sessions"]} 轮**',
        f'**平均复盘质量**：**{data["avg_quality"]}/100**',
        f'**高频标签**：{tags_str}',
        '',
        '## 每日学习记录',
        daily_detail,
        '',
        '## 复盘记录',
        review_detail,
        '',
        '> 注：AI 服务不可用，以上为本地数据摘要。配置 API Key 后可生成深度分析报告。',
    ]
    if error_line:
        lines.append(error_line)
    return '\n'.join(lines)


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

        # 生成数据（含复盘明细）
        data = _build_report_data(report_type)

        type_names = {'daily': '日报', 'weekly': '周报', 'monthly': '月报', 'quarterly': '季报', 'yearly': '年报'}
        name = type_names.get(report_type, report_type)

        # 构建每日学习明细
        daily_lines = []
        for r in data.get('records', []):
            daily_lines.append(f"  - {r.get('date', '?')}：学习 {r.get('study', 0)} 小时")
        daily_detail = '\n'.join(daily_lines) if daily_lines else '  暂无记录'

        # 构建复盘明细（时间、学科、标签、评分）
        review_detail_lines = []
        for entry in data.get('review_records', []):
            review_detail_lines.append(
                f"  - {entry.get('time', '?')} | 学科:{entry.get('subject', '未记录')} | 标签:{entry.get('label', '')} | 评分:{entry.get('score', '?')}/100"
            )
        review_detail_text = '\n'.join(review_detail_lines) if review_detail_lines else '  暂无复盘记录'

        # 标签分布
        tags_str = ', '.join(f'{t}({c}次)' for t, c in data.get('top_tags', [])) or '无'

        prompt = (
            f"你是专业的学习分析顾问。请根据以下详细数据生成一份有深度的{name}，字数不少于 400 字。\n"
            f"时间范围：{data['date_range']}，共 {data['days']} 天。\n"
            f"\n"
            f"## 核心数据\n"
            f"- 总学习时长：{data['total_study_hours']} 小时（{data['sessions']} 轮）\n"
            f"- 平均复盘质量：{data['avg_quality']}/100\n"
            f"- 高频标签：{tags_str}\n"
            f"\n"
            f"## 每日学习明细\n"
            f"{daily_detail}\n"
            f"\n"
            f"## 复盘记录（每条 = 1小时学习后的自评）\n"
            f"{review_detail_text}\n"
            f"\n"
            f"## 格式要求\n"
            f"1. 用 ## 标题分节，结构清晰\n"
            f"2. 关键数字用 **粗体** 突出\n"
            f"3. 用 - 列表项，不要用表格\n"
            f"4. 每段 2-4 行，要有实质内容，不要空泛\n"
            f"5. 建议中要结合具体的评分、学科、标签数据\n"
            f"\n"
            f"## 必须包含的 5 个章节\n"
            f"### 概览\n"
            f"总结本周期学习时长、完成轮次、复盘质量，用数据说话。\n"
            f"\n"
            f"### 趋势分析\n"
            f"分析学习时长的日/周变化趋势，哪些天表现好/差，结合复盘评分解释原因。\n"
            f"\n"
            f"### 学科分布\n"
            f"根据复盘中的学科和标签分布，分析各学科投入情况。\n"
            f"\n"
            f"### 改进建议（5-7条，每条要有具体行动）\n"
            f"基于数据提出可落地的改进建议。\n"
            f"\n"
            f"### 亮点总结\n"
            f"肯定本周期的成就和进步，指出可保持的优点。\n"
        )

        result = _call_ai(prompt)

        if result.get('ok'):
            report_text = result['content']
            # 持久化缓存
            try:
                cache = {'data': data, 'report': report_text, 'generated_at': datetime.now().isoformat(), 'provider': result.get('provider', '')}
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(cache, f, ensure_ascii=False, indent=2)
            except Exception as e:
                log.warning(f'[generate_report] 缓存写入失败: {e}')
            return {'ok': True, 'content': report_text}

        # AI 不可用，返回本地降级报告
        log.warning(f'[generate_report] AI 不可用，使用本地降级报告：{result.get("error", "")}')
        data['ai_error'] = result.get('error', '')
        fallback = _local_fallback_report(report_type, data)
        return {'ok': True, 'content': fallback, 'from_cache': False, 'fallback': True, 'ai_error': result.get('error', '')}

    except Exception as e:
        log.error(f'[generate_report] 报告生成失败: {e}')
        return {'ok': False, 'error': f'报告生成失败：{e}'}

class _ReportWorker(QThread):
    """后台线程：生成 AI 报告，不阻塞 UI"""
    result_ready = pyqtSignal(dict)

    def __init__(self, parent=None, report_type=None, force_refresh=False):
        super().__init__(parent)
        self.report_type = report_type
        self.force_refresh = force_refresh

    def run(self):
        try:
            result = generate_report(self.report_type, force_refresh=self.force_refresh)
            self.result_ready.emit(result)
        except Exception as e:
            log.error(f'[ReportWorker] 报告生成异常: {e}')
            self.result_ready.emit({"ok": False, "error": f"报告生成异常：{e}"})


def _create_app_icon():
    """从 cute_icon.png 加载应用图标，并为托盘/任务栏/窗口各尺寸预生成 pixmap。

    Windows 托盘需要 16x16，任务栏需要 32x32，窗口标题 16x16，Alt-Tab 48x48。
    只提供单一大图时 Qt 自动缩放可能发虚，因此显式加入常用尺寸。
    """
    from PyQt5.QtGui import QPixmap
    icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.png')
    if os.path.exists(icon_path):
        source = QPixmap(icon_path)
        if not source.isNull():
            icon = QIcon()
            for size in (16, 24, 32, 48, 64, 128, 256):
                icon.addPixmap(
                    source.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                    QIcon.Normal,
                    QIcon.Off
                )
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
        ai_providers = self.app_settings.get('ai_providers', [])
        log.info(f'[AI] legacy sensenova_key={bool(sn_key)} agnes_key={bool(ag_key)} providers={len(ai_providers)}')

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

        # 自动备份定时器（每小时检查，24h未备份则执行）
        self._backup_timer = QTimer(self)
        self._backup_timer.timeout.connect(self._check_and_backup)
        self._backup_timer.start(3600 * 1000)

        # 迁移旧 AI key 到 ai_providers（幂等）
        _init_ai_providers()


        self.drag_position = None

        # UI 引用字典（init_ui 中填充）
        self._today_refs = {}

        # 状态机字段预初始化
        self._rest_end_time = None

        # ── 环境音播放器 ──
        self._ambient_player = AmbientPlayer()
        ambient_setting = self.app_settings.get('ambient_sound', '')
        ambient_vol = self.app_settings.get('ambient_volume', 50)
        self._ambient_player.set_volume(ambient_vol)

        # ── 飞书日程管理器（必须在 init_ui 之前，_build_general_tab 会读取） ──
        self._calendar_mgr = FeishuCalendarManager(refresh_interval=300)
        self._calendar_enabled = self.app_settings.get('feishu_calendar', False)
        self._calendar_mgr.enabled = self._calendar_enabled
        self._calendar_tick = 0

        self.init_ui()
        # 创建托盘卡片（浮球点击入口，与主界面分开）
        self._tray_card = TrayCardWidget(self)
        self._tray_card.action_requested.connect(self._on_card_action)
        self._update_tray_card()
        self.update_study_display()
        self.init_tray()
        self.set_autostart(True)
        self.setup_timer()
        # 创建小浮球
        self.floating_ball = FloatingBall(self)
        # 创建5分钟倒计时浮层
        self.countdown_overlay = CountdownOverlay()
        # 20-20-20 护眼提醒
        self.eye_rest_overlay = EyeRestOverlay()
        self._last_eye_rest_time = None

        # 启动时先定位到屏幕右侧，主窗口默认隐藏（只显示小浮球）
        self.position_to_right()
        if not self.app_settings.get('silent_start', False):
            self.show()
        # 恢复上次运行状态（跨重启续接）
        self._restore_active_state()
        # 启动飞书日程（设置开启时才拉取）
        if self._calendar_enabled:
            self._calendar_mgr.start()
        # 恢复环境音设置
        if ambient_setting and ambient_setting in _AMBIENT_SOUNDS:
            QTimer.singleShot(1000, lambda: self._ambient_player.play(ambient_setting))
        # 首次引导（新用户）
        if not self.app_settings.get('onboarding_shown', False):
            QTimer.singleShot(500, self._show_onboarding)
        else:
            # 启动时提示设目标
            self._prompt_goal()

        # 启动时静默检查成就（解锁历史已达标但未触发的）
        QTimer.singleShot(2000, lambda: self._check_achievements(silent=True))

    def init_ui(self):
        self.setWindowTitle(f'休息提醒 {VERSION}')
        self.widget_width = 960
        self.widget_height = 680
        self.setGeometry(100, 100, self.widget_width, self.widget_height)

        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowMinimizeButtonHint)

        self.app_icon = _create_app_icon()
        self.setWindowIcon(self.app_icon)
        self.setObjectName('mainWindow')

        # 强制任务栏显示图标（FramelessWindowHint 在 Windows 上可能导致图标丢失）
        self._taskbar_forced = False

        # ═══ 应用主题 ═══
        theme_pref = self.app_settings.get('theme', 'dark')
        self._current_theme = _resolve_theme(theme_pref)
        self._theme_stylesheet = _apply_theme_stylesheet(self._current_theme)

        # ═══ 应用主题样式（THEMES 系统统一生成，dark/light 一致，无硬编码底层） ═══
        self.setStyleSheet(self._theme_stylesheet)

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

        # Logo / 品牌（矢量闪电，取代 emoji 保证跨机器一致）
        logo = QLabel()
        logo.setFixedSize(40, 40)
        logo.setAlignment(Qt.AlignCenter)
        logo.setStyleSheet('background: transparent;')
        _pm = QPixmap(40, 40)
        _pm.fill(Qt.transparent)
        _p = QPainter(_pm)
        _p.setRenderHint(QPainter.Antialiasing)
        _bolt = QPainterPath()
        _bolt.moveTo(33, 18); _bolt.lineTo(22, 34); _bolt.lineTo(29, 34)
        _bolt.lineTo(27, 46); _bolt.lineTo(38, 30); _bolt.lineTo(31, 30)
        _bolt.closeSubpath()
        _grad = QLinearGradient(22, 18, 38, 46)
        _grad.setColorAt(0.0, QColor(240, 200, 112))
        _grad.setColorAt(1.0, QColor(212, 168, 83))
        _p.setBrush(QBrush(_grad))
        _p.setPen(QPen(QColor(212, 168, 83), 0.5))
        _p.drawPath(_bolt)
        _p.end()
        logo.setPixmap(_pm)
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
        ver_lbl = QLabel(VERSION)
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

        # 构建各 tab — 首屏只加载"今日"，其余延迟加载
        self._tabs_built = {0: False, 1: False, 2: False, 3: False, 4: False}
        self._build_general_tab()      # index 0: 今日概览（首屏必须）
        self._tabs_built[0] = True
        # 其余 tab 用占位 widget，切到时才真正构建
        for i in range(1, 5):
            placeholder = QLabel('加载中...')
            placeholder.setAlignment(Qt.AlignCenter)
            placeholder.setStyleSheet('color: #666; font-size: 14px; background: #0d0d12;')
            self._tab_content.addWidget(placeholder)

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

    def _force_taskbar_icon(self):
        """通过 Win32 API 强制在任务栏显示图标"""
        if self._taskbar_forced:
            return
        try:
            hwnd = int(self.winId())
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            user32 = ctypes.windll.user32
            style = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            # 移除 TOOLWINDOW 标志（隐藏任务栏图标）
            style = style & ~WS_EX_TOOLWINDOW
            # 添加 APPWINDOW 标志（强制显示任务栏图标）
            style = style | WS_EX_APPWINDOW
            user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            self._taskbar_forced = True
            log.info('[任务栏] 已强制显示任务栏图标')
        except Exception as e:
            log.warning(f'[任务栏] 强制图标失败: {e}')

    def showEvent(self, event):
        super().showEvent(event)
        # 窗口首次显示时强制任务栏图标
        QTimer.singleShot(50, self._force_taskbar_icon)



    def _enter_rest(self):
        """手动进入休息状态（快捷键触发）"""
        self._study_countdown_active = False
        self.countdown_overlay.hide_overlay()
        now = datetime.now()
        # 立即记录学习时长（防止崩溃丢失）
        if self.app_settings.get('study_tracking', True):
            self.study_hours_today = round(self.study_hours_today + 1.0, 2)
            self.update_study_display()
        self.timer_state = 'resting'
        self._rest_end_time = now + timedelta(minutes=5)
        self._pending_review = True
        if self.app_settings.get('review_reminder', True):
            self._prompt_review()
        self._sync_buttons()
        log.info('[计时] 快捷键触发：手动进入休息')
        self.tray_icon.showMessage('☕ 快捷键', '已进入休息时间', QSystemTrayIcon.Information, 2000)

    def _load_heatmap_data(self):
        """加载 52 周热力图数据"""
        history = history_store.load()
        today = datetime.now().date()
        # 找到本周日（周日作为一周结束）
        days_since_sunday = (today.weekday() + 1) % 7
        end_of_week = today + timedelta(days=(6 - days_since_sunday))
        # 往前推 52 周 + 当周 = 53 列
        start_date = end_of_week - timedelta(weeks=52, days=end_of_week.weekday())
        data = {}
        total_study = 0
        total_days = 0
        d = start_date
        while d <= today:
            iso = d.isoformat()
            study = history.get(iso, {}).get('study', 0)
            if study > 0:
                data[iso] = study
                total_study += study
                total_days += 1
            d += timedelta(days=1)
        self._heatmap_widget._data = data
        self._heatmap_widget._start_date = start_date
        self._heatmap_widget._end_date = today
        if hasattr(self, '_heatmap_total_lbl'):
            self._heatmap_total_lbl.setText(f'近一年学习 {total_study:.0f}h，{total_days} 天')
        self._heatmap_widget.update()

    def _paint_heatmap(self, event):
        """绘制 GitHub 风格热力图"""
        w = self._heatmap_widget
        p = QPainter(w)
        p.setRenderHint(QPainter.Antialiasing)
        pw, ph = w.width(), w.height()
        data = w._data
        start = getattr(w, '_start_date', None)
        end = getattr(w, '_end_date', None)
        if not start or not end:
            p.end()
            return

        # 计算网格: 53 列 x 7 行
        cols = 53
        rows = 7
        cell_size = min(int((pw - 30) / cols), int((ph - 20) / rows), 12)
        gap = 2
        total_w = cols * (cell_size + gap)
        offset_x = (pw - total_w) // 2
        offset_y = 4

        # 颜色梯度
        colors = ['#161b22', '#0e4429', '#006d32', '#26a641', '#39d353']
        max_study = max(data.values(), default=1)
        if max_study < 1:
            max_study = 1

        w._cell_rects = []

        # 绘制月份标签
        p.setPen(QColor('#555'))
        p.setFont(QFont('Consolas', 7))
        last_month = -1

        d = start
        col = 0
        while d <= end and col < cols:
            weekday = d.weekday()  # 0=Mon, 6=Sun
            row = (weekday + 1) % 7  # 转为 Sun=0, Mon=1, ...

            x = offset_x + col * (cell_size + gap)
            y = offset_y + row * (cell_size + gap)

            iso = d.isoformat()
            study = data.get(iso, 0)
            if study > 0:
                intensity = min(4, int(study / max_study * 4) + 1)
            else:
                intensity = 0
            color = QColor(colors[intensity])

            p.setBrush(QBrush(color))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(x, y, cell_size, cell_size, 2, 2)

            # 存储 rect 用于 tooltip
            rect = QRect(x, y, cell_size, cell_size)
            w._cell_rects.append((rect, iso, study))

            # 月份标签
            if d.month != last_month and d.day <= 7:
                month_names = ['', '1月', '2月', '3月', '4月', '5月', '6月',
                               '7月', '8月', '9月', '10月', '11月', '12月']
                p.setPen(QColor('#555'))
                p.setFont(QFont('Microsoft YaHei', 7))
                p.drawText(x, offset_y + 7 * (cell_size + gap) + 10, month_names[d.month])
                last_month = d.month

            # 下一天
            d += timedelta(days=1)
            if weekday == 6:  # 周日结束，下一列
                col += 1

        p.end()

    def _heatmap_tooltip(self, event):
        """热力图 hover 提示"""
        w = self._heatmap_widget
        pos = event.pos()
        for rect, iso, study in getattr(w, '_cell_rects', []):
            if rect.contains(pos):
                hours = f'{study:.1f}h' if study > 0 else '无学习'
                QToolTip.showText(w.mapToGlobal(pos), iso + chr(10) + hours, w, rect, 2000)
                return
        QToolTip.hideText()

    def _switch_tab(self, name):
        """切换 tab（侧边栏按钮选中 + 延迟加载 + stacked widget 切换）"""
        for n, btn in self._tab_buttons.items():
            btn.setChecked(n == name)
        idx = self.TAB_NAMES.index(name)
        # 延迟加载：首次切换到该 tab 时才构建
        if not self._tabs_built.get(idx, False):
            self._build_tab_on_demand(idx)
            self._tabs_built[idx] = True
        self._tab_content.setCurrentIndex(idx)
        # 更新窗口标题以反映当前 tab
        title_map = {'今日': '📊 今日', 'AI 报告': '🤖 AI 学习报告', '趋势': '📈 学习趋势', '设置': '⚙️ 设置', '关于': 'ℹ️ 关于'}
        self.setWindowTitle(f'休息提醒 {VERSION} — {title_map.get(name, name)}')

    def _build_tab_on_demand(self, idx):
        """延迟构建指定 tab，替换占位 widget"""
        # 先移除占位
        old_widget = self._tab_content.widget(idx)
        if old_widget:
            self._tab_content.removeWidget(old_widget)
            old_widget.deleteLater()
        # 构建真正的 tab
        if idx == 1:
            self._build_ai_tab()
        elif idx == 2:
            self._build_trend_tab()
        elif idx == 3:
            self._build_settings_tab()
        elif idx == 4:
            self._build_about_tab()

    def _build_general_tab(self):
        """今日 tab：学习概览 + 今日数据"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        self._today_refs = {}
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
        # 计时器标签（始终创建，由 _refresh_general_tab 每秒更新）
        timer_lbl = QLabel('')
        timer_lbl.setObjectName('timerLabel')
        timer_lbl.setStyleSheet('color: #6a8cbb; font-size: 12px;')
        sc.addWidget(timer_lbl)
        layout.addWidget(status_card)
        layout.addSpacing(8)
        self._today_refs['state_lbl'] = state_lbl
        self._today_refs['timer_lbl'] = timer_lbl

        # ── 飞书日程卡片 ──
        cal_card = QFrame()
        cal_card.setObjectName('statCard')
        cal_layout = QVBoxLayout(cal_card)
        cal_layout.setContentsMargins(16, 14, 16, 14)
        cal_layout.setSpacing(6)
        # 标题行 + 刷新按钮
        cal_title_row = QHBoxLayout()
        cal_title = QLabel('📅 飞书日程')
        cal_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold;')
        cal_title_row.addWidget(cal_title)
        cal_title_row.addStretch()
        cal_refresh_btn = QPushButton('🔄')
        cal_refresh_btn.setFixedSize(28, 28)
        cal_refresh_btn.setCursor(Qt.PointingHandCursor)
        cal_refresh_btn.setToolTip('手动刷新日程')
        cal_refresh_btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; font-size: 13px; } QPushButton:hover { background: rgba(212,168,83,0.15); }')
        cal_refresh_btn.clicked.connect(self._manual_refresh_calendar)
        cal_title_row.addWidget(cal_refresh_btn)
        cal_layout.addLayout(cal_title_row)
        cal_status = QLabel(self._calendar_mgr.get_display_text() if self._calendar_enabled else '未启用')
        cal_status.setObjectName('calStatusLabel')
        cal_status.setWordWrap(True)
        cal_status.setStyleSheet('color: #6a8cbb; font-size: 12px;')
        cal_layout.addWidget(cal_status)
        # 今日日程列表（最多显示 5 条）
        cal_list = QLabel('')
        cal_list.setObjectName('calListLabel')
        cal_list.setWordWrap(True)
        cal_list.setStyleSheet('color: #888; font-size: 11px;')
        cal_layout.addWidget(cal_list)
        self._today_refs['cal_status'] = cal_status
        self._today_refs['cal_list'] = cal_list
        self._today_refs['cal_card'] = cal_card
        if self._calendar_enabled:
            self._update_calendar_list()
        layout.addWidget(cal_card)
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
        cd_bar.setTextVisible(False)
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
    def _switch_theme(self, theme_key):
        """切换主题 — 即时生效，无需重启"""
        self.app_settings['theme'] = theme_key
        LocalSync.save_settings(self.app_settings)
        resolved = _resolve_theme(theme_key)
        theme_name = THEMES[resolved]['name']
        # 重新生成主题 stylesheet
        self._current_theme = resolved
        self._theme_stylesheet = _apply_theme_stylesheet(resolved)
        # 重新应用到主窗口（直接用主题 stylesheet，无硬编码底层）
        self.setStyleSheet(self._theme_stylesheet)
        # 更新按钮状态（使用新主题色）
        t = THEMES[resolved]
        active_style = f'QPushButton {{ background: {t["accent_bg"]}; color: {t["accent"]}; border: 1px solid {t["accent"]}33; border-radius: 8px; font-size: 12px; font-weight: bold; }} QPushButton:hover {{ background: {t["accent_bg"]}; }}'
        base_style = f'QPushButton {{ background: {t["btn_bg"]}; color: {t["text_secondary"]}; border: 1px solid {t["border"]}; border-radius: 8px; font-size: 12px; }} QPushButton:hover {{ background: {t["btn_hover"]}; }}'
        for key, btn in self._theme_btns.items():
            btn.setChecked(key == theme_key)
            btn.setStyleSheet(active_style if key == theme_key else base_style)
        self._toast('🎨 主题', f'已切换为{theme_name}主题')
        self._toast('设置', '已保存配置')

    def _toggle_silent_start(self, checked):
        self.app_settings['silent_start'] = checked == 1
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')

    def _toggle_close_to_tray(self, checked):
        self.app_settings['close_to_tray'] = checked == 1
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')

    def _toggle_study_tracking(self, checked):
        self.app_settings['study_tracking'] = checked == 1
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')

    def _toggle_review_reminder(self, checked):
        self.app_settings['review_reminder'] = checked == 1
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')

    def _toggle_sound(self, checked):
        self.app_settings['sound_enabled'] = checked == 1
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')

    def _toggle_feishu_calendar(self, checked):
        self._calendar_enabled = (checked == 1)
        self.app_settings['feishu_calendar'] = self._calendar_enabled
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')
        self._calendar_mgr.enabled = self._calendar_enabled
        if self._calendar_enabled:
            self._calendar_mgr.start()
            self.tray_icon.showMessage('📅 飞书日程', '已开启日程同步', QSystemTrayIcon.Information, 3000)
        else:
            self._calendar_mgr.stop()
            self.tray_icon.showMessage('📅 飞书日程', '已关闭日程同步', QSystemTrayIcon.Information, 3000)
        self._refresh_calendar_display()

    def _manual_refresh_calendar(self):
        """手动刷新飞书日程"""
        if not self._calendar_enabled:
            self._toast('📅 飞书日程', '日程同步未启用')
            return
        self._toast('📅 飞书日程', '正在刷新...')
        self._calendar_mgr.refresh()

    def _update_calendar_list(self):
        """更新今日 tab 中的日程列表文本"""
        try:
            refs = getattr(self, '_today_refs', {})
            cal_list = refs.get('cal_list')
            if not cal_list or sip.isdeleted(cal_list):
                return
            events = self._calendar_mgr.get_today_events()
            if not events:
                cal_list.setText('今日暂无日程安排')
                return
            from feishu_calendar import _TZ_CST
            now = datetime.now(_TZ_CST)
            lines = []
            for evt in events[:6]:
                status = evt.status_at(now)
                marker = '🟢' if status == 'ongoing' else ('⏳' if status == 'upcoming' else '✔')
                lines.append(f'{marker} {evt.time_range}  {evt.summary}')
            cal_list.setText('\n'.join(lines))
        except Exception:
            pass

    def _refresh_calendar_display(self):
        """刷新日程卡片的状态文本和列表"""
        try:
            refs = getattr(self, '_today_refs', {})
            cal_status = refs.get('cal_status')
            if cal_status and not sip.isdeleted(cal_status):
                if self._calendar_enabled:
                    cal_status.setText(self._calendar_mgr.get_display_text())
                else:
                    cal_status.setText('未启用')
            self._update_calendar_list()
        except Exception:
            pass

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
        # 强制刷新按钮
        refresh_btn = QPushButton('🔄 强制刷新')
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: rgba(106,140,187,0.1); color: #6a8cbb;
                border: 1px solid rgba(106,140,187,0.2); border-radius: 100px;
                padding: 8px 16px; font-size: 12px;
            }
            QPushButton:hover { background: rgba(106,140,187,0.2); }
        """)
        refresh_btn.clicked.connect(self._force_refresh_report)
        btn_row.addWidget(refresh_btn)
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
        self._current_report_type = report_type  # 记住当前类型，供强制刷新用
        # 空状态：无学习数据时显示引导，不调 AI
        history = history_store.load() or {}
        if not history:
            t = THEMES.get(self._current_theme, THEMES['dark'])
            self._report_view.setHtml(
                f'<div style="text-align:center; padding:48px 20px;">'
                f'<p style="color:{t["accent"]}; font-size:13px; margin:0 0 14px;">AI 学习报告</p>'
                f'<p style="color:{t["text_secondary"]}; font-size:14px; margin:0 0 10px;">还没有学习记录</p>'
                f'<p style="color:{t["text_muted"]}; font-size:12px; margin:0; line-height:1.7;">'
                f'完成第一次 60 分钟学习后<br/>AI 会在这里为你生成个性化报告</p>'
                f'</div>'
            )
            return
        self._report_view.setHtml('<p style="color:#888;">⏳ 正在生成报告...</p>')

        # 禁用按钮防止重复点击
        for b in self._report_buttons.values():
            b.setEnabled(False)

        # 取消旧的 worker（防止竞态）
        if hasattr(self, '_report_worker') and self._report_worker is not None:
            self._report_worker.quit()
            self._report_worker.wait()

        worker = _ReportWorker(self, report_type, force_refresh)
        self._report_worker = worker
        def _on_done(result):
            self._report_worker = None
            for b in self._report_buttons.values():
                b.setEnabled(True)
            if result.get("ok"):
                self._report_view.setHtml(_md_to_html(result['content']))
            elif result.get("error"):
                self._report_view.setHtml(f'<p style="color:#c95454;">⚠️ AI 请求失败: {result["error"]}</p><p style="color:#888;">点击「刷新」重试。</p>')
        worker.result_ready.connect(_on_done)
        worker.start()

    def _force_refresh_report(self):
        """强制刷新当前 AI 报告（忽略缓存）"""
        rtype = getattr(self, '_current_report_type', 'daily')
        self._load_report(rtype, force_refresh=True)

    def _build_trend_tab(self):
        """趋势 tab：带时间选择器的学习趋势图 + 时段热力图"""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标题行
        title_row = QHBoxLayout()
        h1 = QLabel('学习趋势')
        h1.setFont(QFont('Georgia, "Noto Serif SC", serif', 20, QFont.Bold))
        title_row.addWidget(h1)
        title_row.addStretch()
        layout.addLayout(title_row)
        sub = QLabel('可视化你的学习节奏和专注度')
        sub.setStyleSheet('color: #666; font-size: 13px;')
        layout.addWidget(sub)
        layout.addSpacing(4)

        # ═══ 时间选择器 ═══
        period_row = QHBoxLayout()
        period_row.setSpacing(6)
        self._trend_period = 7  # 默认7天
        self._trend_period_btns = {}
        period_style_base = 'QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-family: "Microsoft YaHei"; }'
        period_style_active = 'QPushButton { background: rgba(212,168,83,0.12); color: #d4a853; border: 1px solid rgba(212,168,83,0.25); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-weight: bold; font-family: "Microsoft YaHei"; }'
        for days, label in [(7, '近7天'), (14, '近14天'), (30, '近30天')]:
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(period_style_active if days == 7 else period_style_base)
            btn.clicked.connect(lambda checked, d=days: self._switch_trend_period(d))
            period_row.addWidget(btn)
            self._trend_period_btns[days] = btn
        # 自定义按钮
        custom_btn = QPushButton('自定义')
        custom_btn.setFixedHeight(30)
        custom_btn.setCursor(Qt.PointingHandCursor)
        custom_btn.setStyleSheet(period_style_base)
        custom_btn.clicked.connect(self._pick_custom_trend_period)
        period_row.addWidget(custom_btn)
        self._trend_period_btns['custom'] = custom_btn
        period_row.addStretch()
        # 日期范围标签
        self._trend_range_lbl = QLabel('')
        self._trend_range_lbl.setStyleSheet('color: #666; font-size: 11px; font-family: Consolas;')
        period_row.addWidget(self._trend_range_lbl)
        layout.addLayout(period_row)
        layout.addSpacing(4)

        # ═══ 趋势图卡片 ═══
        trend_card = QFrame()
        trend_card.setObjectName('statCard')
        tc_layout = QVBoxLayout(trend_card)
        tc_layout.setContentsMargins(16, 14, 16, 14)
        tc_layout.setSpacing(8)

        # 图表区域（动态高度）
        self._trend_chart = QWidget()
        self._trend_chart.setMinimumHeight(160)
        self._trend_chart.setStyleSheet('background: transparent;')
        self._trend_chart._bar_rects = []
        self._trend_chart._days_data = []
        tc_layout.addWidget(self._trend_chart)

        # 图例 + 汇总行
        summary_row = QHBoxLayout()
        summary_row.setSpacing(16)
        dot = QLabel()
        dot.setFixedSize(10, 10)
        dot.setStyleSheet('background: #78B450; border-radius: 5px;')
        summary_row.addWidget(dot)
        legend = QLabel('学习时长')
        legend.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        summary_row.addWidget(legend)
        self._trend_summary = QLabel('')
        self._trend_summary.setStyleSheet('color: #6a8cbb; font-size: 12px; font-weight: bold; background: transparent;')
        summary_row.addWidget(self._trend_summary)
        summary_row.addStretch()
        # 轮次标记
        dot2 = QLabel()
        dot2.setFixedSize(10, 10)
        dot2.setStyleSheet('background: #d4a853; border-radius: 5px;')
        summary_row.addWidget(dot2)
        self._trend_rounds_lbl = QLabel('')
        self._trend_rounds_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        summary_row.addWidget(self._trend_rounds_lbl)
        tc_layout.addLayout(summary_row)
        layout.addWidget(trend_card)

        # ═══ 时段评分热力图 ═══
        self._heat_card = QFrame()
        self._heat_card.setObjectName('statCard')
        hc = QVBoxLayout(self._heat_card)
        hc.setContentsMargins(16, 14, 16, 14)
        hc.setSpacing(8)

        self._heat_title = QLabel('🕐 时段评分分布')
        self._heat_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold;')
        hc.addWidget(self._heat_title)

        self._heat_widget = QWidget()
        self._heat_widget.setFixedHeight(140)
        self._heat_widget.setStyleSheet('background: transparent;')
        self._heat_widget._bucket_info = []
        hc.addWidget(self._heat_widget)

        # 图例
        leg_row = QHBoxLayout()
        leg_row.setSpacing(12)
        for txt, color in [('高分区', '#51cf66'), ('中等', '#fcc419'), ('低分区', '#ff8844'), ('无数据', '#1e1e26')]:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            d = QLabel()
            d.setFixedSize(10, 10)
            d.setStyleSheet(f'background: {color}; border-radius: 2px;')
            row_layout.addWidget(d)
            l = QLabel(txt)
            l.setStyleSheet('color: #666; font-size: 11px; background: transparent;')
            row_layout.addWidget(l)
            leg_row.addWidget(row)
        leg_row.addStretch()
        hc.addLayout(leg_row)
        layout.addWidget(self._heat_card)
        layout.addSpacing(8)

        # ── GitHub 风格学习热力图 ──
        gh_title = QLabel('🔥 学习热力图（近 52 周）')
        gh_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold;')
        layout.addWidget(gh_title)

        self._heatmap_widget = QWidget()
        self._heatmap_widget.setFixedHeight(120)
        self._heatmap_widget.setStyleSheet('background: transparent;')
        self._heatmap_widget._data = {}
        self._heatmap_widget._cell_rects = []
        layout.addWidget(self._heatmap_widget)

        # 热力图图例
        gh_leg = QHBoxLayout()
        gh_leg.setSpacing(4)
        gh_leg.addWidget(QLabel('少'))
        for intensity, color in [(0, '#161b22'), (1, '#0e4429'), (2, '#006d32'), (3, '#26a641'), (4, '#39d353')]:
            sq = QLabel()
            sq.setFixedSize(12, 12)
            sq.setStyleSheet(f'background: {color}; border-radius: 2px;')
            gh_leg.addWidget(sq)
        gh_leg.addWidget(QLabel('多'))
        gh_leg.addStretch()
        self._heatmap_total_lbl = QLabel('')
        self._heatmap_total_lbl.setStyleSheet('color: #888; font-size: 11px;')
        gh_leg.addWidget(self._heatmap_total_lbl)
        layout.addLayout(gh_leg)

        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

        # 绑定 paint事件
        self._trend_chart.paintEvent = self._paint_trend_chart
        self._trend_chart.mouseMoveEvent = self._trend_chart_tooltip
        self._trend_chart.setMouseTracking(True)
        self._heat_widget.paintEvent = self._paint_heat_map

        # 热力图绑定
        self._heatmap_widget.paintEvent = self._paint_heatmap
        self._heatmap_widget.mouseMoveEvent = self._heatmap_tooltip
        self._heatmap_widget.setMouseTracking(True)

        # 初始绘制
        self._switch_trend_period(7)
        self._load_heatmap_data()

    def _switch_trend_period(self, days):
        """切换趋势图时间范围"""
        self._trend_period = days
        # 更新按钮样式
        active_style = 'QPushButton { background: rgba(212,168,83,0.12); color: #d4a853; border: 1px solid rgba(212,168,83,0.25); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-weight: bold; font-family: "Microsoft YaHei"; }'
        base_style = 'QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-family: "Microsoft YaHei"; }'
        for key, btn in self._trend_period_btns.items():
            if key == days:
                btn.setStyleSheet(active_style)
            else:
                btn.setStyleSheet(base_style)
        self._refresh_trend_data(days)

    def _pick_custom_trend_period(self):
        """弹出日期范围选择对话框"""
        from PyQt5.QtWidgets import QDateEdit
        from PyQt5.QtCore import QDate
        dialog = QDialog(self)
        dialog.setWindowTitle('选择日期范围')
        dialog.setFixedSize(320, 180)
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.setStyleSheet('QDialog { background: #0d0d12; color: #e8e4dc; } QLabel { color: #e8e4dc; font-size: 13px; } QDateEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 8px; padding: 8px; font-size: 13px; } QPushButton { background: #d4a853; color: #0d0d12; border: none; border-radius: 8px; padding: 8px 24px; font-weight: bold; font-size: 13px; } QPushButton:hover { background: #e8bc6a; }')
        dl = QVBoxLayout(dialog)
        dl.setContentsMargins(20, 16, 20, 16)
        dl.setSpacing(12)
        dl.addWidget(QLabel('选择日期范围'))
        row1 = QHBoxLayout()
        row1.addWidget(QLabel('开始'))
        start_edit = QDateEdit()
        start_edit.setDate(QDate.currentDate().addDays(-30))
        start_edit.setCalendarPopup(True)
        row1.addWidget(start_edit)
        dl.addLayout(row1)
        row2 = QHBoxLayout()
        row2.addWidget(QLabel('结束'))
        end_edit = QDateEdit()
        end_edit.setDate(QDate.currentDate())
        end_edit.setCalendarPopup(True)
        row2.addWidget(end_edit)
        dl.addLayout(row2)
        ok_btn = QPushButton('确定')
        ok_btn.setCursor(Qt.PointingHandCursor)
        def on_ok():
            s = start_edit.date().toPyDate()
            e = end_edit.date().toPyDate()
            if s > e:
                s, e = e, s
            self._trend_custom_range = (s, e)
            # 高亮自定义按钮
            active_style = 'QPushButton { background: rgba(212,168,83,0.12); color: #d4a853; border: 1px solid rgba(212,168,83,0.25); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-weight: bold; font-family: "Microsoft YaHei"; }'
            base_style = 'QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 6px 16px; font-size: 12px; font-family: "Microsoft YaHei"; }'
            for key, btn in self._trend_period_btns.items():
                btn.setStyleSheet(active_style if key == 'custom' else base_style)
            self._trend_period = 'custom'
            self._refresh_trend_data('custom')
            dialog.accept()
        ok_btn.clicked.connect(on_ok)
        dl.addWidget(ok_btn, alignment=Qt.AlignRight)
        dialog.exec_()

    def _refresh_trend_data(self, period):
        """根据时间范围加载数据并刷新图表"""
        today = datetime.now().date()
        history = history_store.load()

        if period == 'custom' and hasattr(self, '_trend_custom_range'):
            start_date, end_date = self._trend_custom_range
            days_count = (end_date - start_date).days + 1
            range_text = f'{start_date.strftime("%m/%d")} - {end_date.strftime("%m/%d")}'
        else:
            days_count = period
            start_date = today - timedelta(days=days_count - 1)
            end_date = today
            range_text = f'{start_date.strftime("%m/%d")} - {end_date.strftime("%m/%d")}'

        self._trend_range_lbl.setText(range_text)

        # 加载每日数据
        days_data = []
        total_study = 0
        total_rounds = 0
        for i in range(days_count):
            d = start_date + timedelta(days=i)
            iso = d.isoformat()
            rec = history.get(iso, {})
            study = rec.get('study', 0)
            rounds = rec.get('rounds', 0)
            total_study += study
            total_rounds += rounds
            # 标签：少于14天显示日期，多于14天只显示部分
            if days_count <= 14:
                label = d.strftime('%m/%d')
            elif i % (days_count // 10 + 1) == 0 or i == days_count - 1:
                label = d.strftime('%m/%d')
            else:
                label = ''
            days_data.append({'label': label, 'study': study, 'rounds': rounds, 'date': d.isoformat()})

        self._trend_chart._days_data = days_data
        self._trend_summary.setText(f'共 {total_study:.1f}h')
        self._trend_rounds_lbl.setText(f'{total_rounds} 轮')
        self._heat_title.setText(f'🕐 时段评分分布（近{days_count}天复盘）')

        # 热力图数据
        buckets_data = _aggregate_reviews_by_time(review_store.load(), days=days_count)
        bucket_labels = [b[0] for b in _build_time_buckets()]
        all_scores = [s for scores in buckets_data.values() for s in scores]
        is_old = _is_old_format(all_scores) if all_scores else False
        bucket_info = []
        for label in bucket_labels:
            scores = buckets_data[label]
            count = len(scores)
            if count > 0:
                avg = sum(scores) / count
                norm = avg / 5 if is_old else avg / 100
                norm = max(0, min(1, norm))
            else:
                avg, norm = 0, 0
            bucket_info.append((label, avg, count, norm))
        self._heat_widget._bucket_info = bucket_info

        # 失效 QPixmap 缓存（数据变了需要重绘）
        self._trend_chart._cache_pixmap = None
        self._heat_widget._cache_pixmap = None

        self._trend_chart.update()
        self._heat_widget.update()

    def _paint_trend_chart(self, event):
        """绘制趋势柱状图（带 QPixmap 缓存，数据不变时直接复用）"""
        chart = self._trend_chart
        # 缓存检查：尺寸相同且已有缓存则直接绘制缓存
        cache = getattr(chart, '_cache_pixmap', None)
        cache_size = getattr(chart, '_cache_size', None)
        cur_size = (chart.width(), chart.height())
        if cache is not None and cache_size == cur_size:
            p = QPainter(chart)
            p.drawPixmap(0, 0, cache)
            p.end()
            return
        # 重新绘制到 QPixmap
        pixmap = QPixmap(chart.width(), chart.height())
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = chart.width(), chart.height()
        days = chart._days_data
        n = len(days)
        if n == 0:
            t = THEMES.get(self._current_theme, THEMES['dark'])
            # 矢量闪电图标（淡化，暗示"待激活"）
            p.save()
            p.setOpacity(0.22)
            p.translate(w // 2 - 15, h // 2 - 28)
            p.scale(0.6, 0.6)
            bolt = QPainterPath()
            bolt.moveTo(33, 18); bolt.lineTo(22, 34); bolt.lineTo(29, 34)
            bolt.lineTo(27, 46); bolt.lineTo(38, 30); bolt.lineTo(31, 30)
            bolt.closeSubpath()
            p.setBrush(QBrush(QColor(t['accent'])))
            p.setPen(Qt.NoPen)
            p.drawPath(bolt)
            p.restore()
            # 引导文案
            p.setPen(QColor(t['text_muted']))
            p.setFont(QFont('Microsoft YaHei', 10))
            p.drawText(QRect(0, h // 2 + 12, w, 28), Qt.AlignCenter, '开始第一次学习，趋势图会在这里生长')
            p.end()
            return

        vals = [d['study'] for d in days]
        mx = max(max(vals, default=0), 1)
        # 自适应柱子宽度
        bw = max(4, min(28, int((w - 60) / (n * 1.5))))
        gap = max(2, int((w - 40 - n * bw) / (n + 1)))
        bottom = h - 30
        ch = bottom - 16
        chart._bar_rects = []

        # 绘制网格线
        for frac in [0.25, 0.5, 0.75, 1.0]:
            y = bottom - int(ch * frac)
            p.setPen(QPen(QColor(255, 255, 255, 8), 1, Qt.DotLine))
            p.drawLine(20, y, w - 20, y)
            p.setPen(QColor('#333'))
            p.setFont(QFont('Consolas', 7))
            p.drawText(2, y + 3, f'{mx * frac:.1f}')

        for i, d in enumerate(days):
            x = 20 + gap + i * (bw + gap)
            bh = max(2, int(d['study'] / mx * ch)) if d['study'] > 0 else 0

            # 柱子颜色渐变
            if d['study'] > 0:
                gradient = QLinearGradient(x, bottom - bh, x, bottom)
                gradient.setColorAt(0, QColor('#8BC34A'))
                gradient.setColorAt(1, QColor('#558B2F'))
                p.setBrush(QBrush(gradient))
            else:
                p.setBrush(QBrush(QColor(40, 40, 50)))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(x, bottom - max(bh, 2), bw, max(bh, 2), 2, 2)
            chart._bar_rects.append((QRect(x, bottom - max(bh, 2), bw, max(bh, 2)), d.get('label', ''), d['study'], d.get('date', '')))

            # X轴标签
            if d['label']:
                p.setPen(QColor('#555'))
                p.setFont(QFont('Microsoft YaHei', 7))
                tw = p.fontMetrics().width(d['label'])
                p.drawText(x + bw // 2 - tw // 2, bottom + 16, d['label'])

            # 柱顶数值
            if d['study'] > 0 and bw >= 10:
                p.setPen(QColor('#78B450'))
                p.setFont(QFont('Consolas', 7, QFont.Bold))
                vt = f"{d['study']:.1f}"
                tw = p.fontMetrics().width(vt)
                p.drawText(x + bw // 2 - tw // 2, bottom - bh - 4, vt)
        p.end()
        # 缓存 pixmap 并绘制到 widget
        chart._cache_pixmap = pixmap
        chart._cache_size = (chart.width(), chart.height())
        painter = QPainter(chart)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

    def _trend_chart_tooltip(self, event):
        """趋势图 hover 提示"""
        chart = self._trend_chart
        pos = event.pos()
        for rect, label, value, date in chart._bar_rects:
            if rect.contains(pos):
                tip = f'{date}  学习 {value:.1f}h' if date else f'{label}  {value:.1f}h'
                QToolTip.showText(chart.mapToGlobal(pos), tip, chart, rect, 2000)
                return
        QToolTip.hideText()

    def _paint_heat_map(self, event):
        """绘制时段评分热力图（带 QPixmap 缓存）"""
        widget = self._heat_widget
        # 缓存检查
        cache = getattr(widget, '_cache_pixmap', None)
        cache_size = getattr(widget, '_cache_size', None)
        cur_size = (widget.width(), widget.height())
        if cache is not None and cache_size == cur_size:
            p = QPainter(widget)
            p.drawPixmap(0, 0, cache)
            p.end()
            return
        # 重新绘制到 QPixmap
        pixmap = QPixmap(widget.width(), widget.height())
        pixmap.fill(Qt.transparent)
        p = QPainter(pixmap)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = widget.width(), widget.height()
        bucket_info = widget._bucket_info
        n = len(bucket_info)
        if n == 0:
            p.end()
            return
        col_w = max(40, int((w - 20) / n))
        total_cols_w = n * col_w
        start_x = (w - total_cols_w) // 2
        bar_h = h - 40
        for i, (label, avg, count, norm) in enumerate(bucket_info):
            x = start_x + i * col_w + 4
            bw = col_w - 8
            if count > 0:
                r = int(255 * (1 - norm))
                g = int(200 * norm + 55)
                fill = QColor(r, g, 30)
                fill.setAlpha(120 + int(135 * norm))
                p.setBrush(QBrush(fill))
                p.setPen(Qt.NoPen)
                bh = max(4, int(bar_h * norm))
                p.drawRoundedRect(x, h - 32 - bh, bw, bh, 3, 3)
                p.setPen(QColor('#e8e4dc'))
                p.setFont(QFont('Microsoft YaHei', 8, QFont.Bold))
                p.drawText(x + bw // 2 - 8, h - 36 - bh, f'{avg:.0f}')
            else:
                p.setBrush(QBrush(QColor(30, 30, 38)))
                p.setPen(Qt.NoPen)
                p.drawRoundedRect(x, h - 32 - 4, bw, 4, 2, 2)
            p.setPen(QColor('#555'))
            p.setFont(QFont('Microsoft YaHei', 7))
            tw = p.fontMetrics().width(label)
            p.drawText(x + bw // 2 - tw // 2, h - 12, label)
            if count > 0:
                p.setPen(QColor('#444'))
                ct = f'{count}次'
                tw2 = p.fontMetrics().width(ct)
                p.drawText(x + bw // 2 - tw2 // 2, h - 22, ct)
        p.end()
        # 缓存 pixmap 并绘制到 widget
        widget._cache_pixmap = pixmap
        widget._cache_size = (widget.width(), widget.height())
        painter = QPainter(widget)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()

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

        # ═══ 外观 ═══
        layout.addLayout(self._make_section_header('🎨', '外观'))

        theme_card = QFrame()
        theme_card.setObjectName('sectionCard')
        theme_layout_inner = QVBoxLayout(theme_card)
        theme_layout_inner.setContentsMargins(14, 12, 14, 12)
        theme_layout_inner.setSpacing(8)

        theme_header = QHBoxLayout()
        theme_icon = QLabel('🎨')
        theme_icon.setFixedSize(20, 20)
        theme_icon.setStyleSheet('background: transparent;')
        theme_header.addWidget(theme_icon)
        theme_title = QLabel('主题切换')
        theme_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold; font-family: "Microsoft YaHei"; background: transparent;')
        theme_header.addWidget(theme_title)
        theme_header.addStretch()
        theme_hint = QLabel('切换后需重启应用')
        theme_hint.setStyleSheet('color: #555; font-size: 11px; background: transparent;')
        theme_header.addWidget(theme_hint)
        theme_layout_inner.addLayout(theme_header)

        theme_btn_row = QHBoxLayout()
        theme_btn_row.setSpacing(8)
        self._theme_btns = {}
        current_theme_pref = self.app_settings.get('theme', 'dark')
        theme_options = [
            ('dark', '🌙 深色'),
            ('light', '☀️ 浅色'),
            ('system', '💻 跟随系统'),
        ]
        for key, label in theme_options:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            is_active = current_theme_pref == key
            btn.setChecked(is_active)
            if is_active:
                btn.setStyleSheet('QPushButton { background: rgba(212,168,83,0.15); color: #d4a853; border: 1px solid rgba(212,168,83,0.3); border-radius: 8px; font-size: 12px; font-weight: bold; } QPushButton:hover { background: rgba(212,168,83,0.25); }')
            else:
                btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(255,255,255,0.08); }')
            btn.clicked.connect(lambda checked, k=key: self._switch_theme(k))
            theme_btn_row.addWidget(btn)
            self._theme_btns[key] = btn
        theme_layout_inner.addLayout(theme_btn_row)
        layout.addWidget(theme_card)

        layout.addSpacing(8)

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

        # ═══ 飞书集成 ═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('🔗', '飞书集成'))

        feishu_cal_checked = self.app_settings.get('feishu_calendar', False)
        feishu_cal_row = self._make_setting_row(
            '📅', '飞书日程同步',
            '实时显示当前/下一个飞书日程，每5分钟自动刷新',
            feishu_cal_checked,
            self._toggle_feishu_calendar
        )
        layout.addWidget(feishu_cal_row)

        # ═══ 环境白噪音 ═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('🎵', '环境白噪音'))

        amb_card = QFrame()
        amb_card.setObjectName('sectionCard')
        amb_layout = QVBoxLayout(amb_card)
        amb_layout.setContentsMargins(14, 12, 14, 12)
        amb_layout.setSpacing(8)

        # 音效选择按钮行
        amb_btn_row = QHBoxLayout()
        amb_btn_row.setSpacing(6)
        self._ambient_btns = {}
        current_ambient = self.app_settings.get('ambient_sound', '')
        for key, (label, _, _) in _AMBIENT_SOUNDS.items():
            btn = QPushButton(label)
            btn.setFixedHeight(30)
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
            is_active = current_ambient == key and self._ambient_player.is_playing
            if is_active:
                btn.setChecked(True)
                btn.setStyleSheet('QPushButton { background: rgba(212,168,83,0.15); color: #d4a853; border: 1px solid rgba(212,168,83,0.3); border-radius: 8px; font-size: 12px; font-weight: bold; } QPushButton:hover { background: rgba(212,168,83,0.25); }')
            else:
                btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(255,255,255,0.08); }')
            btn.clicked.connect(lambda checked, k=key: self._toggle_ambient(k))
            amb_btn_row.addWidget(btn)
            self._ambient_btns[key] = btn
        # 关闭按钮
        stop_btn = QPushButton('关闭')
        stop_btn.setFixedHeight(30)
        stop_btn.setCursor(Qt.PointingHandCursor)
        stop_btn.setStyleSheet('QPushButton { background: rgba(201,84,84,0.1); color: #c95454; border: 1px solid rgba(201,84,84,0.2); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(201,84,84,0.2); }')
        stop_btn.clicked.connect(self._stop_ambient)
        amb_btn_row.addWidget(stop_btn)
        amb_layout.addLayout(amb_btn_row)

        # 音量滑块
        vol_row = QHBoxLayout()
        vol_row.setSpacing(8)
        vol_lbl = QLabel('🔉')
        vol_lbl.setFixedWidth(20)
        vol_lbl.setStyleSheet('background: transparent;')
        vol_row.addWidget(vol_lbl)
        vol_slider = QSlider(Qt.Horizontal)
        vol_slider.setRange(0, 100)
        vol_slider.setValue(self.app_settings.get('ambient_volume', 50))
        vol_slider.setFixedHeight(20)
        vol_slider.setStyleSheet('QSlider::groove:horizontal { background: #333; border-radius: 4px; height: 8px; } QSlider::handle:horizontal { background: #d4a853; border-radius: 8px; width: 16px; height: 16px; margin: -4px 0; } QSlider::sub-page:horizontal { background: #d4a853; border-radius: 4px; }')
        vol_slider.valueChanged.connect(self._set_ambient_volume)
        vol_row.addWidget(vol_slider, 1)
        self._ambient_vol_lbl = QLabel(f'{vol_slider.value()}%')
        self._ambient_vol_lbl.setStyleSheet('color: #888; font-size: 11px; font-family: Consolas; background: transparent;')
        self._ambient_vol_lbl.setFixedWidth(36)
        vol_row.addWidget(self._ambient_vol_lbl)
        amb_layout.addLayout(vol_row)

        layout.addWidget(amb_card)

        # ═══ 每周报告邮件 ═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('📧', '每周报告邮件'))

        mail_card = QFrame()
        mail_card.setObjectName('sectionCard')
        mail_layout = QVBoxLayout(mail_card)
        mail_layout.setContentsMargins(14, 12, 14, 12)
        mail_layout.setSpacing(6)

        mail_desc = QLabel('每周一早上通过 Agent QQ 邮箱自动发送 AI 学习分析报告')
        mail_desc.setStyleSheet('color: #555; font-size: 11px; font-family: "Microsoft YaHei"; background: transparent;')
        mail_layout.addWidget(mail_desc)

        # 收件人
        rcp_row = QHBoxLayout()
        rcp_row.setSpacing(6)
        rcp_row.addWidget(QLabel('收件人'))
        rcp_input = QLineEdit()
        rcp_input.setPlaceholderText('your@email.com')
        rcp_input.setText(self.app_settings.get('mail_recipient', ''))
        rcp_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 8px; padding: 6px 10px; font-size: 12px; }')
        rcp_row.addWidget(rcp_input, 1)
        mail_layout.addLayout(rcp_row)

        # 保存 + 测试发送按钮
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._mail_status_lbl = QLabel('')
        self._mail_status_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        btn_row.addWidget(self._mail_status_lbl)
        btn_row.addStretch()
        test_btn = QPushButton('测试发送')
        test_btn.setFixedHeight(30)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet('QPushButton { background: rgba(106,140,187,0.1); color: #6a8cbb; border: 1px solid rgba(106,140,187,0.2); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(106,140,187,0.2); }')
        test_btn.clicked.connect(lambda: self._send_test_email(rcp_input))
        btn_row.addWidget(test_btn)
        save_mail_btn = QPushButton('保存配置')
        save_mail_btn.setFixedHeight(30)
        save_mail_btn.setCursor(Qt.PointingHandCursor)
        save_mail_btn.setStyleSheet('QPushButton { background: #d4a853; color: #0d0d12; border: none; border-radius: 8px; font-weight: bold; font-size: 12px; } QPushButton:hover { background: #e8bc6a; }')
        save_mail_btn.clicked.connect(lambda: self._save_mail_config(rcp_input))
        btn_row.addWidget(save_mail_btn)
        mail_layout.addLayout(btn_row)

        # 开关
        mail_toggle_row = self._make_setting_row(
            '📅', '每周一自动发送',
            '每周一 08:00 自动生成并发送上周学习报告',
            self.app_settings.get('mail_weekly_enabled', False),
            self._toggle_weekly_email
        )
        mail_layout.addWidget(mail_toggle_row)

        layout.addWidget(mail_card)

        # ═══ AI 服务（自定义提供商）═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('🤖', 'AI 服务（自定义提供商）'))

        # 迁移旧 key（幂等）
        _init_ai_providers()

        ai_card = QFrame()
        ai_card.setObjectName('sectionCard')
        ai_outer = QVBoxLayout(ai_card)
        ai_outer.setContentsMargins(14, 12, 14, 12)
        ai_outer.setSpacing(8)

        ai_desc = QLabel('支持任何 OpenAI 兼容的 API。添加多个提供商后，按优先级依次尝试。')
        ai_desc.setStyleSheet('color: #555; font-size: 11px; font-family: "Microsoft YaHei"; background: transparent;')
        ai_desc.setWordWrap(True)
        ai_outer.addWidget(ai_desc)

        # 提供商列表容器（动态填充）
        self._ai_providers_container = QVBoxLayout()
        self._ai_providers_container.setSpacing(6)
        ai_outer.addLayout(self._ai_providers_container)
        self._ai_provider_widgets = []  # 保存引用便于读取
        self._refresh_ai_providers_ui()

        # 添加提供商按钮
        add_provider_btn = QPushButton('+ 添加 AI 提供商')
        add_provider_btn.setFixedHeight(32)
        add_provider_btn.setCursor(Qt.PointingHandCursor)
        add_provider_btn.setStyleSheet('QPushButton { background: rgba(212,168,83,0.1); color: #d4a853; border: 1px dashed rgba(212,168,83,0.3); border-radius: 8px; font-size: 12px; font-weight: bold; } QPushButton:hover { background: rgba(212,168,83,0.2); }')
        add_provider_btn.clicked.connect(self._add_ai_provider_ui)
        ai_outer.addWidget(add_provider_btn)

        layout.addWidget(ai_card)

        # ═══ 数据备份 ═══
        layout.addSpacing(8)
        layout.addLayout(self._make_section_header('💾', '数据备份（GitHub 私有仓库）'))

        backup_card = QFrame()
        backup_card.setObjectName('sectionCard')
        backup_layout = QVBoxLayout(backup_card)
        backup_layout.setContentsMargins(14, 12, 14, 12)
        backup_layout.setSpacing(6)

        backup_desc = QLabel('每24小时自动备份学习/复盘/设置等数据到 GitHub 私有仓库，支持一键恢复')
        backup_desc.setStyleSheet('color: #555; font-size: 11px; font-family: "Microsoft YaHei"; background: transparent;')
        backup_desc.setWordWrap(True)
        backup_layout.addWidget(backup_desc)

        # GitHub Token
        token_row = QHBoxLayout()
        token_row.setSpacing(6)
        token_row.addWidget(QLabel('Token'))
        token_input = QLineEdit()
        token_input.setEchoMode(QLineEdit.Password)
        token_input.setPlaceholderText('ghp_...')
        token_input.setText(_decrypt_key(self.app_settings.get('github_backup_token', '')))
        token_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 8px; padding: 6px 10px; font-size: 12px; font-family: Consolas; }')
        token_row.addWidget(token_input, 1)
        backup_layout.addLayout(token_row)

        # 仓库名
        repo_row = QHBoxLayout()
        repo_row.setSpacing(6)
        repo_row.addWidget(QLabel('仓库'))
        repo_input = QLineEdit()
        repo_input.setPlaceholderText('owner/rest-reminder-backup')
        repo_input.setText(self.app_settings.get('backup_repo', 'kuangketongxue/rest-reminder-backup'))
        repo_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 8px; padding: 6px 10px; font-size: 12px; font-family: Consolas; }')
        repo_row.addWidget(repo_input, 1)
        backup_layout.addLayout(repo_row)

        # 上次备份时间
        last_bkp = self.app_settings.get('last_backup_time', 0)
        last_str = datetime.fromtimestamp(last_bkp).strftime('%m/%d %H:%M') if last_bkp else '从未'
        self._backup_status_lbl = QLabel(f'上次备份: {last_str}')
        self._backup_status_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        backup_layout.addWidget(self._backup_status_lbl)

        # 按钮行
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        verify_btn = QPushButton('验证连接')
        verify_btn.setFixedHeight(30)
        verify_btn.setCursor(Qt.PointingHandCursor)
        verify_btn.setStyleSheet('QPushButton { background: rgba(106,140,187,0.1); color: #6a8cbb; border: 1px solid rgba(106,140,187,0.2); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(106,140,187,0.2); }')
        verify_btn.clicked.connect(lambda: self._verify_backup(token_input, repo_input))
        btn_row.addWidget(verify_btn)
        btn_row.addStretch()
        backup_btn = QPushButton('立即备份')
        backup_btn.setFixedHeight(30)
        backup_btn.setCursor(Qt.PointingHandCursor)
        backup_btn.setStyleSheet('QPushButton { background: rgba(120,180,80,0.15); color: #78B450; border: 1px solid rgba(120,180,80,0.3); border-radius: 8px; font-size: 12px; font-weight: bold; } QPushButton:hover { background: rgba(120,180,80,0.25); }')
        backup_btn.clicked.connect(lambda: self._do_backup(token_input, repo_input))
        btn_row.addWidget(backup_btn)
        restore_btn = QPushButton('恢复数据')
        restore_btn.setFixedHeight(30)
        restore_btn.setCursor(Qt.PointingHandCursor)
        restore_btn.setStyleSheet('QPushButton { background: rgba(201,84,84,0.1); color: #c95454; border: 1px solid rgba(201,84,84,0.2); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(201,84,84,0.2); }')
        restore_btn.clicked.connect(lambda: self._do_restore(token_input, repo_input))
        btn_row.addWidget(restore_btn)
        backup_layout.addLayout(btn_row)

        layout.addWidget(backup_card)

        layout.addStretch()
        scroll.setWidget(container)
        self._tab_content.addWidget(scroll)

    def _save_mail_config(self, rcp_input):
        """保存邮件配置"""
        self.app_settings['mail_recipient'] = rcp_input.text().strip()
        LocalSync.save_settings(self.app_settings)
        self._mail_status_lbl.setText('✓ 已保存')
        self._mail_status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
        self._toast('📧 邮件配置', '周报邮件配置已保存')
        self._toast('设置', '已保存配置')

    def _send_test_email(self, rcp_input):
        """测试发送周报邮件"""
        self._save_mail_config(rcp_input)
        recipient = self.app_settings.get('mail_recipient', '')
        if not recipient:
            self._mail_status_lbl.setText('✗ 请填写收件人')
            self._mail_status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')
            return
        self._mail_status_lbl.setText('⏳ 发送中...')
        self._mail_status_lbl.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        self._mail_worker = _WeeklyReportWorker(recipient)
        def on_done(ok, msg):
            if ok:
                self._mail_status_lbl.setText('✓ 发送成功')
                self._mail_status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
                self._toast('设置', '已保存配置')
            else:
                self._mail_status_lbl.setText(f'✗ {msg[:40]}')
                self._mail_status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')
        self._mail_worker.result_ready.connect(on_done)
        self._mail_worker.start()

    def _toggle_weekly_email(self, checked):
        """切换每周自动发送"""
        self.app_settings['mail_weekly_enabled'] = (checked == 1)
        LocalSync.save_settings(self.app_settings)
        if checked == 1:
            self._toast('📧 周报', '已开启每周一自动发送')
        else:
            self._toast('📧 周报', '已关闭每周自动发送')
        self._toast('设置', '已保存配置')

    def _check_weekly_report(self):
        """检查是否需要发送周报（每周一 08:00-09:00）"""
        if not self.app_settings.get('mail_weekly_enabled', False):
            return
        now = datetime.now()
        if now.weekday() != 0:  # 不是周一
            return
        if now.hour != 8:  # 不是 8 点
            return
        # 检查今天是否已发送
        last_sent = self.app_settings.get('mail_last_sent', '')
        if last_sent == now.date().isoformat():
            return
        # 发送
        recipient = self.app_settings.get('mail_recipient', '')
        if not recipient:
            return
        self.app_settings['mail_last_sent'] = now.date().isoformat()
        LocalSync.save_settings(self.app_settings)
        self._mail_worker = _WeeklyReportWorker(recipient)
        self._mail_worker.result_ready.connect(lambda ok, msg: log.info(f'[周报] {msg}'))
        self._mail_worker.start()

    def _toggle_ambient(self, sound_type):
        """切换环境音"""
        if self._ambient_player.is_playing and self._ambient_player._current_sound == sound_type:
            self._stop_ambient()
            self._toast('设置', '已保存配置')
            return
        self._ambient_player.play(sound_type)
        self.app_settings['ambient_sound'] = sound_type
        LocalSync.save_settings(self.app_settings)
        self._toast('设置', '已保存配置')
        # 更新按钮状态
        active_style = 'QPushButton { background: rgba(212,168,83,0.15); color: #d4a853; border: 1px solid rgba(212,168,83,0.3); border-radius: 8px; font-size: 12px; font-weight: bold; } QPushButton:hover { background: rgba(212,168,83,0.25); }'
        base_style = 'QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(255,255,255,0.08); }'
        for key, btn in self._ambient_btns.items():
            btn.setChecked(key == sound_type)
            btn.setStyleSheet(active_style if key == sound_type else base_style)
        self._toast('🎵 环境音', _AMBIENT_SOUNDS[sound_type][0] + ' 已开启')

    def _stop_ambient(self):
        """停止环境音"""
        self._ambient_player.stop()
        self.app_settings['ambient_sound'] = ''
        LocalSync.save_settings(self.app_settings)
        base_style = 'QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; font-size: 12px; } QPushButton:hover { background: rgba(255,255,255,0.08); }'
        for btn in self._ambient_btns.values():
            btn.setChecked(False)
            btn.setStyleSheet(base_style)

    def _set_ambient_volume(self, value):
        """设置环境音音量"""
        self._ambient_player.set_volume(value)
        self.app_settings['ambient_volume'] = value
        LocalSync.save_settings(self.app_settings)
        if hasattr(self, '_ambient_vol_lbl'):
            self._ambient_vol_lbl.setText(f'{value}%')

    def _save_ai_key(self, key_name, key_value, status_label):
        """保存 AI API Key 到 settings（加密存储）—— 旧接口，保留兼容"""
        self.app_settings[key_name] = _encrypt_key(key_value) if key_value else ''
        LocalSync.save_settings(self.app_settings)
        if key_value:
            status_label.setText('✓ 已保存')
            status_label.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
            self._toast('设置', '已保存配置')
        else:
            status_label.setText('未配置')
            status_label.setStyleSheet('color: #fcc419; font-size: 11px; background: transparent;')
            self._toast('设置', '已保存配置')
        log.info(f'[AI] {key_name} updated, len={len(key_value)}')

    # ═══ AI 提供商管理 ═══
    def _refresh_ai_providers_ui(self):
        """刷新 AI 提供商列表 UI"""
        # 清空旧的
        while self._ai_providers_container.count():
            item = self._ai_providers_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._ai_provider_widgets = []

        providers = self.app_settings.get('ai_providers', [])
        for idx, p in enumerate(providers):
            widget = self._build_ai_provider_card(p, idx)
            self._ai_providers_container.addWidget(widget)
            self._ai_provider_widgets.append(widget)

    def _build_ai_provider_card(self, provider, idx):
        """构建单个 AI 提供商卡片"""
        import uuid
        card = QFrame()
        card.setObjectName('sectionCard')
        cl = QVBoxLayout(card)
        cl.setContentsMargins(12, 10, 12, 10)
        cl.setSpacing(6)

        # 第一行：名称 + 启用开关 + 删除按钮
        top_row = QHBoxLayout()
        top_row.setSpacing(6)
        name_input = QLineEdit(provider.get('name', ''))
        name_input.setPlaceholderText('提供商名称（如 SenseNova）')
        name_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 6px; padding: 4px 8px; font-size: 12px; font-weight: bold; }')
        top_row.addWidget(name_input, 2)

        enable_btn = QPushButton('✓ 启用' if provider.get('enabled', True) else '✗ 禁用')
        enable_btn.setFixedHeight(28)
        enable_btn.setCursor(Qt.PointingHandCursor)
        is_enabled = provider.get('enabled', True)
        if is_enabled:
            enable_btn.setStyleSheet('QPushButton { background: rgba(120,180,80,0.15); color: #78B450; border: 1px solid rgba(120,180,80,0.3); border-radius: 6px; font-size: 11px; }')
        else:
            enable_btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); color: #666; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; font-size: 11px; }')
        top_row.addWidget(enable_btn)

        del_btn = QPushButton('删除')
        del_btn.setFixedHeight(28)
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.setStyleSheet('QPushButton { background: rgba(201,84,84,0.1); color: #c95454; border: 1px solid rgba(201,84,84,0.2); border-radius: 6px; font-size: 11px; } QPushButton:hover { background: rgba(201,84,84,0.2); }')
        top_row.addWidget(del_btn)
        cl.addLayout(top_row)

        # 第二行：URL
        url_row = QHBoxLayout()
        url_row.setSpacing(6)
        url_lbl = QLabel('URL')
        url_lbl.setFixedWidth(36)
        url_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        url_row.addWidget(url_lbl)
        url_input = QLineEdit(provider.get('url', ''))
        url_input.setPlaceholderText('https://api.example.com/v1/chat/completions')
        url_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 6px; padding: 4px 8px; font-size: 11px; font-family: Consolas; }')
        url_row.addWidget(url_input, 1)
        cl.addLayout(url_row)

        # 第三行：Model + Key
        mk_row = QHBoxLayout()
        mk_row.setSpacing(6)
        model_lbl = QLabel('模型')
        model_lbl.setFixedWidth(36)
        model_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        mk_row.addWidget(model_lbl)
        model_input = QLineEdit(provider.get('model', ''))
        model_input.setPlaceholderText('模型 ID（如 deepseek-chat）')
        model_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 6px; padding: 4px 8px; font-size: 11px; font-family: Consolas; }')
        mk_row.addWidget(model_input, 1)

        key_input = QLineEdit()
        key_input.setEchoMode(QLineEdit.Password)
        key_input.setPlaceholderText('API Key')
        raw_key = provider.get('api_key', '')
        key_input.setText(_decrypt_key(raw_key) if raw_key else '')
        key_input.setStyleSheet('QLineEdit { background: #16161c; color: #e8e4dc; border: 1px solid #252530; border-radius: 6px; padding: 4px 8px; font-size: 11px; font-family: Consolas; }')
        mk_row.addWidget(key_input, 1)
        cl.addLayout(mk_row)

        # 第四行：测试按钮 + 状态
        test_row = QHBoxLayout()
        test_row.setSpacing(6)
        test_btn = QPushButton('测试连接')
        test_btn.setFixedHeight(28)
        test_btn.setCursor(Qt.PointingHandCursor)
        test_btn.setStyleSheet('QPushButton { background: rgba(106,140,187,0.1); color: #6a8cbb; border: 1px solid rgba(106,140,187,0.2); border-radius: 6px; font-size: 11px; } QPushButton:hover { background: rgba(106,140,187,0.2); }')
        test_row.addWidget(test_btn)
        status_lbl = QLabel('')
        status_lbl.setStyleSheet('color: #888; font-size: 11px; background: transparent;')
        test_row.addWidget(status_lbl, 1)
        cl.addLayout(test_row)

        # 保存引用
        card._name_input = name_input
        card._url_input = url_input
        card._model_input = model_input
        card._key_input = key_input
        card._enable_btn = enable_btn
        card._status_lbl = status_lbl
        card._provider_id = provider.get('id', str(uuid.uuid4()))
        card._enabled = is_enabled

        # 事件
        def toggle_enable():
            card._enabled = not card._enabled
            if card._enabled:
                enable_btn.setText('✓ 启用')
                enable_btn.setStyleSheet('QPushButton { background: rgba(120,180,80,0.15); color: #78B450; border: 1px solid rgba(120,180,80,0.3); border-radius: 6px; font-size: 11px; }')
            else:
                enable_btn.setText('✗ 禁用')
                enable_btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); color: #666; border: 1px solid rgba(255,255,255,0.08); border-radius: 6px; font-size: 11px; }')
            self._save_ai_providers()

        def do_test():
            status_lbl.setText('⏳ 测试中...')
            status_lbl.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
            url = url_input.text().strip()
            model = model_input.text().strip()
            key = key_input.text().strip()
            ok, msg = _test_ai_provider(url, model, key)
            if ok:
                status_lbl.setText(f'✓ {msg}')
                status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
            else:
                status_lbl.setText(f'✗ {msg[:80]}')
                status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')

        def do_delete():
            reply = QMessageBox.question(self, '确认删除', f'确定删除提供商「{name_input.text() or "未命名"}」吗？',
                                          QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                providers = self.app_settings.get('ai_providers', [])
                providers = [p for p in providers if p.get('id') != card._provider_id]
                self.app_settings['ai_providers'] = providers
                LocalSync.save_settings(self.app_settings)
                self._refresh_ai_providers_ui()
                self._toast('🤖 AI 服务', '已删除提供商')

        def on_edit():
            self._save_ai_providers()

        enable_btn.clicked.connect(toggle_enable)
        test_btn.clicked.connect(do_test)
        del_btn.clicked.connect(do_delete)
        name_input.editingFinished.connect(on_edit)
        url_input.editingFinished.connect(on_edit)
        model_input.editingFinished.connect(on_edit)
        key_input.editingFinished.connect(on_edit)

        return card

    def _add_ai_provider_ui(self):
        """添加一个新的 AI 提供商卡片"""
        import uuid
        new_provider = {
            'id': str(uuid.uuid4()),
            'name': '',
            'url': '',
            'model': '',
            'api_key': '',
            'enabled': True,
            'priority': len(self.app_settings.get('ai_providers', [])) + 1,
        }
        providers = self.app_settings.get('ai_providers', [])
        providers.append(new_provider)
        self.app_settings['ai_providers'] = providers
        LocalSync.save_settings(self.app_settings)
        self._refresh_ai_providers_ui()

    def _save_ai_providers(self):
        """从 UI 读取所有提供商配置并保存"""
        providers = []
        for idx, card in enumerate(self._ai_provider_widgets):
            try:
                key_plain = card._key_input.text().strip()
                provider = {
                    'id': card._provider_id,
                    'name': card._name_input.text().strip() or f'提供商{idx+1}',
                    'url': card._url_input.text().strip(),
                    'model': card._model_input.text().strip(),
                    'api_key': _encrypt_key(key_plain) if key_plain else '',
                    'enabled': card._enabled,
                    'priority': idx + 1,
                }
                providers.append(provider)
            except Exception as e:
                log.warning(f'[AI] 保存提供商 {idx} 失败: {e}')
        self.app_settings['ai_providers'] = providers
        LocalSync.save_settings(self.app_settings)
        log.info(f'[AI] 保存 {len(providers)} 个提供商')

    # ═══ 数据备份 ═══
    def _check_and_backup(self):
        """定时检查：距上次备份超过24小时则自动执行"""
        last = self.app_settings.get('last_backup_time', 0)
        if time.time() - last < 86400:  # 24h
            return
        token = _decrypt_key(self.app_settings.get('github_backup_token', ''))
        repo = self.app_settings.get('backup_repo', '')
        if not token or not repo:
            return
        log.info('[备份] 自动备份开始...')
        ok, msg = backup.backup(token, repo)
        if ok:
            self.app_settings['last_backup_time'] = time.time()
            LocalSync.save_settings(self.app_settings)
            # 更新状态标签
            try:
                last_str = datetime.fromtimestamp(time.time()).strftime('%m/%d %H:%M')
                self._backup_status_lbl.setText(f'上次备份: {last_str}')
            except Exception:
                pass
            log.info(f'[备份] 成功: {msg}')
        else:
            log.error(f'[备份] 失败: {msg}')

    def _verify_backup(self, token_input, repo_input):
        """验证 GitHub 连接配置"""
        token = token_input.text().strip()
        repo = repo_input.text().strip()
        self._backup_status_lbl.setText('⏳ 正在验证...')
        self._backup_status_lbl.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        ok, msg = backup.validate_token(token, repo)
        if ok:
            # 保存配置
            self.app_settings['github_backup_token'] = _encrypt_key(token)
            self.app_settings['backup_repo'] = repo
            LocalSync.save_settings(self.app_settings)
            self._backup_status_lbl.setText(msg)
            self._backup_status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
            self._toast('💾 备份', 'GitHub 连接验证成功')
        else:
            self._backup_status_lbl.setText(msg)
            self._backup_status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')

    def _do_backup(self, token_input, repo_input):
        """手动备份"""
        token = token_input.text().strip()
        repo = repo_input.text().strip()
        if not token or not repo:
            self._backup_status_lbl.setText('请填写 Token 和仓库名')
            self._backup_status_lbl.setStyleSheet('color: #fcc419; font-size: 11px; background: transparent;')
            return
        # 先保存
        self.app_settings['github_backup_token'] = _encrypt_key(token)
        self.app_settings['backup_repo'] = repo
        LocalSync.save_settings(self.app_settings)
        self._backup_status_lbl.setText('⏳ 备份中...')
        self._backup_status_lbl.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        ok, msg = backup.backup(token, repo)
        if ok:
            self.app_settings['last_backup_time'] = time.time()
            LocalSync.save_settings(self.app_settings)
            last_str = datetime.fromtimestamp(time.time()).strftime('%m/%d %H:%M')
            self._backup_status_lbl.setText(f'上次备份: {last_str}')
            self._backup_status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
            self._toast('💾 备份', msg)
        else:
            self._backup_status_lbl.setText(f'失败: {msg[:60]}')
            self._backup_status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')

    def _do_restore(self, token_input, repo_input):
        """恢复数据（需用户确认）"""
        token = token_input.text().strip()
        repo = repo_input.text().strip()
        if not token or not repo:
            self._backup_status_lbl.setText('请填写 Token 和仓库名')
            self._backup_status_lbl.setStyleSheet('color: #fcc419; font-size: 11px; background: transparent;')
            return
        # 确认对话框
        reply = QMessageBox.question(
            self, '确认恢复', '⚠️ 此操作将用云端备份覆盖当前本地数据\n\n确定要恢复吗？',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        self._backup_status_lbl.setText('⏳ 恢复中...')
        self._backup_status_lbl.setStyleSheet('color: #6a8cbb; font-size: 11px; background: transparent;')
        ok, msg = backup.restore(token, repo)
        if ok:
            self._backup_status_lbl.setText('恢复成功，请重启应用')
            self._backup_status_lbl.setStyleSheet('color: #78B450; font-size: 11px; background: transparent;')
            self._toast('💾 恢复', msg)
        else:
            self._backup_status_lbl.setText(f'失败: {msg[:60]}')
            self._backup_status_lbl.setStyleSheet('color: #c95454; font-size: 11px; background: transparent;')

    def _build_about_tab(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet('QScrollArea { border: none; background: #0d0d12; }')
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # ═══ 品牌 Hero 区 ═══
        hero = QFrame()
        hero.setStyleSheet('QFrame { background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #16161c, stop:1 #1a1a24); border: 1px solid #252530; border-radius: 16px; }')
        hero_layout = QVBoxLayout(hero)
        hero_layout.setContentsMargins(24, 24, 24, 24)
        hero_layout.setSpacing(8)

        # Logo + 名称
        brand_row = QHBoxLayout()
        logo = QLabel('⚡')
        logo.setFont(QFont('Segoe UI Emoji', 32))
        logo.setStyleSheet('background: transparent;')
        brand_row.addWidget(logo)
        brand_col = QVBoxLayout()
        brand_col.setSpacing(2)
        name_lbl = QLabel('休息提醒')
        name_lbl.setFont(QFont('Georgia, "Noto Serif SC", serif', 22, QFont.Bold))
        name_lbl.setStyleSheet('color: #e8e6e1; background: transparent;')
        brand_col.addWidget(name_lbl)
        tagline = QLabel('专注计时 · 休息提醒 · AI 学习分析')
        tagline.setStyleSheet('color: #888; font-size: 12px; background: transparent;')
        brand_col.addWidget(tagline)
        brand_row.addLayout(brand_col)
        brand_row.addStretch()
        # 版本 badge
        ver_badge = QLabel(VERSION)
        ver_badge.setStyleSheet('background: rgba(212,168,83,0.12); color: #d4a853; border: 1px solid rgba(212,168,83,0.2); border-radius: 8px; padding: 4px 14px; font-size: 12px; font-family: Consolas; font-weight: bold;')
        brand_row.addWidget(ver_badge)
        hero_layout.addLayout(brand_row)

        # 操作按钮行（扁平化）
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        btn_row.setContentsMargins(0, 8, 0, 0)
        for text, slot, tip_color in [
            ('🌐 官网', self._open_website, '#6a8cbb'),
            ('🐱 GitHub', self._open_github, '#78B450'),
            ('📋 更新日志', self._show_changelog, '#d4a853'),
            ('🔄 检查更新', self._check_update, '#d97757'),
        ]:
            btn = QPushButton(text)
            btn.setFixedHeight(32)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f'QPushButton {{ background: rgba(255,255,255,0.04); color: {tip_color}; border: 1px solid rgba(255,255,255,0.06); border-radius: 8px; padding: 0 14px; font-size: 12px; }} QPushButton:hover {{ background: rgba(255,255,255,0.08); }}')
            btn.clicked.connect(slot)
            btn_row.addWidget(btn)
        hero_layout.addLayout(btn_row)
        layout.addWidget(hero)

        # ═══ 系统状态（两列：环境 + 数据） ═══
        status_row = QHBoxLayout()
        status_row.setSpacing(12)

        # ── 左列：环境诊断 ──
        env_card = QFrame()
        env_card.setObjectName('sectionCard')
        ec = QVBoxLayout(env_card)
        ec.setContentsMargins(16, 14, 16, 14)
        ec.setSpacing(4)
        env_header = QHBoxLayout()
        env_h_icon = QLabel('🔍')
        env_h_icon.setStyleSheet('background: transparent; font-size: 14px;')
        env_header.addWidget(env_h_icon)
        env_h_title = QLabel('环境')
        env_h_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold; background: transparent;')
        env_header.addWidget(env_h_title)
        env_header.addStretch()
        refresh_btn = QPushButton('刷新')
        refresh_btn.setFixedSize(48, 24)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.setStyleSheet('QPushButton { background: rgba(255,255,255,0.04); color: #888; border: 1px solid rgba(255,255,255,0.06); border-radius: 6px; font-size: 11px; } QPushButton:hover { background: rgba(255,255,255,0.08); color: #ccc; }')
        refresh_btn.clicked.connect(self._refresh_env_check)
        env_header.addWidget(refresh_btn)
        ec.addLayout(env_header)

        env_items = [
            ('Python', self._check_python),
            ('PyQt5', self._check_pyqt5),
            ('平台', self._check_platform),
            ('内存', self._check_memory),
            ('磁盘', self._check_disk),
        ]
        for name, check_fn in env_items:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel('●')
            dot.setStyleSheet('color: #333; font-size: 10px; background: transparent;')
            dot.setFixedWidth(14)
            row.addWidget(dot)
            n = QLabel(name)
            n.setStyleSheet('color: #aaa; font-size: 13px; background: transparent;')
            n.setFixedWidth(48)
            row.addWidget(n)
            v = QLabel('…')
            v.setStyleSheet('color: #6a8cbb; font-size: 13px; font-family: Consolas; background: transparent;')
            v.setObjectName(f'env_{name}')
            row.addWidget(v)
            row.addStretch()
            ec.addLayout(row)
        status_row.addWidget(env_card)

        # ── 右列：数据 + AI ──
        right_col = QVBoxLayout()
        right_col.setSpacing(12)

        # 数据文件卡片
        data_card = QFrame()
        data_card.setObjectName('sectionCard')
        dc = QVBoxLayout(data_card)
        dc.setContentsMargins(16, 14, 16, 14)
        dc.setSpacing(4)
        data_header = QHBoxLayout()
        data_h_icon = QLabel('💾')
        data_h_icon.setStyleSheet('background: transparent; font-size: 14px;')
        data_header.addWidget(data_h_icon)
        data_h_title = QLabel('数据')
        data_h_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold; background: transparent;')
        data_header.addWidget(data_h_title)
        data_header.addStretch()
        dc.addLayout(data_header)

        data_items = [
            ('学习记录', '.daily_log.json'),
            ('复盘记录', '.review_log.json'),
            ('设置', '.settings.json'),
            ('连续打卡', '.streak.json'),
            ('历史统计', '.stats_history.json'),
        ]
        base_dir = os.path.dirname(os.path.abspath(__file__))
        for name, filename in data_items:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel('●')
            dot.setStyleSheet('color: #333; font-size: 10px; background: transparent;')
            dot.setFixedWidth(14)
            row.addWidget(dot)
            n = QLabel(name)
            n.setStyleSheet('color: #aaa; font-size: 13px; background: transparent;')
            n.setFixedWidth(56)
            row.addWidget(n)
            fpath = os.path.join(base_dir, filename)
            if os.path.exists(fpath):
                size = os.path.getsize(fpath)
                size_str = f'{size} B' if size < 1024 else f'{size/1024:.1f} KB'
                s = QLabel(size_str)
                s.setStyleSheet('color: #78B450; font-size: 13px; font-family: Consolas; background: transparent;')
            else:
                s = QLabel('—')
                s.setStyleSheet('color: #444; font-size: 13px; background: transparent;')
            row.addWidget(s)
            row.addStretch()
            dc.addLayout(row)
        right_col.addWidget(data_card)

        # AI 服务状态卡片
        ai_card = QFrame()
        ai_card.setObjectName('sectionCard')
        aic = QVBoxLayout(ai_card)
        aic.setContentsMargins(16, 14, 16, 14)
        aic.setSpacing(6)
        ai_header = QHBoxLayout()
        ai_h_icon = QLabel('🤖')
        ai_h_icon.setStyleSheet('background: transparent; font-size: 14px;')
        ai_header.addWidget(ai_h_icon)
        ai_h_title = QLabel('AI 服务')
        ai_h_title.setStyleSheet('color: #e8e6e1; font-size: 13px; font-weight: bold; background: transparent;')
        ai_header.addWidget(ai_h_title)
        ai_header.addStretch()
        aic.addLayout(ai_header)

        sn_key = self.app_settings.get('sensenova_api_key', '')
        ag_key = self.app_settings.get('agnes_api_key', '') or os.environ.get('AGNES_API_KEY', '')
        for provider, has_key in [('SenseNova', bool(sn_key)), ('Agnes AI', bool(ag_key))]:
            row = QHBoxLayout()
            row.setSpacing(6)
            dot = QLabel('●')
            dot.setStyleSheet(f'color: {"#78B450" if has_key else "#444"}; font-size: 10px; background: transparent;')
            dot.setFixedWidth(14)
            row.addWidget(dot)
            pname = QLabel(provider)
            pname.setStyleSheet('color: #888; font-size: 13px; background: transparent;')
            pname.setFixedWidth(70)
            row.addWidget(pname)
            pstatus = QLabel('✓ 已配置' if has_key else '未配置')
            pstatus.setStyleSheet(f'color: {"#78B450" if has_key else "#555"}; font-size: 13px; background: transparent;')
            row.addWidget(pstatus)
            row.addStretch()
            aic.addLayout(row)

        if not sn_key and not ag_key:
            ai_hint = QLabel('→ 设置 tab “AI 服务”区域可配置 API Key')
            ai_hint.setStyleSheet('color: #fcc419; font-size: 13px; background: transparent; padding-top: 2px;')
            aic.addWidget(ai_hint)

        right_col.addWidget(ai_card)
        status_row.addLayout(right_col)

        layout.addLayout(status_row)
        layout.addSpacing(8)

        # ── 成就收藏 ──
        ach_title_row = QHBoxLayout()
        ach_h = QLabel('🏅 成就')
        ach_h.setFont(QFont('Georgia, "Noto Serif SC", serif', 14, QFont.Bold))
        ach_title_row.addWidget(ach_h)
        ach_title_row.addStretch()
        ach_count = QLabel('')
        ach_count.setStyleSheet('color: #888; font-size: 12px; font-family: Consolas;')
        ach_title_row.addWidget(ach_count)
        layout.addLayout(ach_title_row)

        ach_card = QFrame()
        ach_card.setObjectName('sectionCard')
        ach_layout = QVBoxLayout(ach_card)
        ach_layout.setContentsMargins(16, 14, 16, 14)
        ach_layout.setSpacing(6)

        earned_data = achievements_store.load().get('earned', {})
        total_earned = len(earned_data)
        total_all = len(_ACHIEVEMENTS)
        fill_pct_val = int(total_earned / max(total_all, 1) * 100)
        ach_count.setText(f'{total_earned}/{total_all} · {fill_pct_val}%')

        # 全成就达成彩蛋
        if total_all > 0 and total_earned == total_all:
            crown_lbl = QLabel('👑 全成就达成！你是真正的学习王者')
            crown_lbl.setStyleSheet('color: #d4a853; font-size: 14px; font-weight: bold; font-family: "Microsoft YaHei"; background: transparent; padding: 4px 0;')
            crown_lbl.setAlignment(Qt.AlignCenter)
            ach_layout.addWidget(crown_lbl)

        # 总进度条（QProgressBar 自适应宽度）
        progress_bar = QProgressBar()
        progress_bar.setRange(0, 100)
        progress_bar.setValue(fill_pct_val)
        progress_bar.setTextVisible(False)
        progress_bar.setFixedHeight(6)
        progress_bar.setStyleSheet(
            'QProgressBar { background: rgba(255,255,255,8); border-radius: 3px; border: none; }'
            'QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #d4a853, stop:1 #e8bc6a); border-radius: 3px; }'
        )
        ach_layout.addWidget(progress_bar)

        # 获取当前成就数据用于进度显示
        ach_stats = self._get_achievement_stats()

        categories = {}
        for ach in _ACHIEVEMENTS:
            cat = ach['category']
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(ach)

        cat_names = {'study': '学习时长', 'streak': '连续打卡',
                     'daily': '单日成就', 'review': '复盘质量',
                     'rounds': '学习轮次'}

        for cat_key, cat_label in cat_names.items():
            achs = categories.get(cat_key, [])
            if not achs:
                continue
            cat_lbl = QLabel(cat_label)
            cat_lbl.setStyleSheet('color: #888; font-size: 13px; font-weight: bold; background: transparent; padding-top: 4px;')
            ach_layout.addWidget(cat_lbl)

            # 网格布局：每行最多 4 个，自动换行
            grid = QGridLayout()
            grid.setSpacing(6)
            for idx, ach in enumerate(achs):
                row = idx // 4
                col = idx % 4
                is_earned = ach['id'] in earned_data
                card = QFrame()
                card.setFixedHeight(52)
                card.setCursor(Qt.PointingHandCursor)
                if is_earned:
                    # 今日解锁的成就加金色脉冲边框
                    earned_date_full = earned_data[ach['id']]
                    earned_date = earned_date_full[:10]
                    today_str = datetime.now().date().isoformat()
                    if earned_date == today_str:
                        card.setStyleSheet(
                            'QFrame { background: rgba(212,168,83,25); border: 2px solid #d4a853; border-radius: 8px; }')
                    else:
                        card.setStyleSheet(
                            'QFrame { background: rgba(212,168,83,15); border: 1px solid rgba(212,168,83,30); border-radius: 8px; }')
                    card.setToolTip(f'{ach["name"]}\n{ach["desc"]}\n解锁: {earned_date}')
                else:
                    card.setStyleSheet(
                        'QFrame { background: rgba(255,255,255,4); border: 1px solid rgba(255,255,255,8); border-radius: 8px; }')
                    card.setToolTip(f'{ach["name"]}\n{ach["desc"]}\n(未解锁)')

                cl = QVBoxLayout(card)
                cl.setContentsMargins(8, 4, 8, 4)
                cl.setSpacing(2)
                top_row = QHBoxLayout()
                icon_lbl = QLabel(ach['icon'])
                icon_lbl.setStyleSheet('background: transparent; font-size: 14px;')
                top_row.addWidget(icon_lbl)
                name_lbl = QLabel(ach['name'])
                name_lbl.setStyleSheet(f'color: {"#d4a853" if is_earned else "#666"}; font-size: 11px; font-weight: bold; background: transparent;')
                top_row.addWidget(name_lbl)
                top_row.addStretch()
                cl.addLayout(top_row)

                # 进度信息：已解锁显示日期，未解锁显示差额
                prog = ach_stats.get(ach['id'], {})
                if is_earned:
                    info_lbl = QLabel(f'✓ {earned_date}')
                    info_lbl.setStyleSheet('color: #78B450; font-size: 10px; font-family: Consolas; background: transparent;')
                elif prog.get('progress_text'):
                    remaining = prog['target'] - prog['current']
                    unit = prog.get('unit', '')
                    if remaining > 0:
                        info_text = f'差 {remaining}{unit} · {int(prog["pct"]*100)}%'
                    else:
                        info_text = prog['progress_text']
                    info_lbl = QLabel(info_text)
                    info_lbl.setStyleSheet('color: #555; font-size: 10px; font-family: Consolas; background: transparent;')
                else:
                    info_lbl = QLabel(ach['desc'])
                    info_lbl.setStyleSheet('color: #555; font-size: 10px; background: transparent;')
                cl.addWidget(info_lbl)

                grid.addWidget(card, row, col)

            ach_layout.addLayout(grid)

        layout.addWidget(ach_card)

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
        """显示更新日志（从 CHANGELOG.md 读取）"""
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
        changelog_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'CHANGELOG.md')
        try:
            with open(changelog_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception:
            text = '无法读取 CHANGELOG.md'
        dialog = QDialog(self)
        dialog.setWindowTitle('📋 更新日志')
        dialog.setFixedSize(560, 480)
        dialog.setStyleSheet("""
            QDialog { background-color: #0c0c10; color: #e8e6e1; }
            QTextBrowser { background: #14141a; color: #e8e6e1; border: 1px solid #222; border-radius: 8px; padding: 12px; font-size: 13px; font-family: Consolas; }
        """)
        layout = QVBoxLayout(dialog)
        browser = QTextBrowser()
        browser.setPlainText(text)
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
        self._check_memory()
        self._check_disk()

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
                lbl.setStyleSheet('color: #ff4444; font-size: 13px; font-family: Consolas;')

    def _check_platform(self):
        lbl = self.findChild(QLabel, 'env_平台')
        if lbl:
            lbl.setText(f'{platform.system()} {platform.machine()}')

    def _check_memory(self):
        lbl = self.findChild(QLabel, 'env_内存')
        if lbl:
            try:
                mem = psutil.virtual_memory()
                used_gb = mem.used / (1024**3)
                total_gb = mem.total / (1024**3)
                pct = mem.percent
                color = '#ff4444' if pct > 90 else '#fcc419' if pct > 75 else '#78B450'
                lbl.setText(f'{used_gb:.1f} / {total_gb:.0f} GB ({pct}%)')
                lbl.setStyleSheet(f'color: {color}; font-size: 12px; font-family: Consolas;')
            except Exception:
                lbl.setText('检测失败')

    def _check_disk(self):
        lbl = self.findChild(QLabel, 'env_磁盘')
        if lbl:
            try:
                disk = psutil.disk_usage(os.path.dirname(os.path.abspath(__file__)))
                free_gb = disk.free / (1024**3)
                total_gb = disk.total / (1024**3)
                pct = disk.percent
                color = '#ff4444' if pct > 95 else '#fcc419' if pct > 85 else '#78B450'
                lbl.setText(f'剩余 {free_gb:.1f} GB / 共 {total_gb:.0f} GB ({100-pct:.0f}% 可用)')
                lbl.setStyleSheet(f'color: {color}; font-size: 12px; font-family: Consolas;')
            except Exception:
                lbl.setText('检测失败')

    def _diagnose_env(self):
        """诊断环境状态"""
        from PyQt5.QtWidgets import QMessageBox
        diag_lines = [
            f'Python {platform.python_version()}',
            f'平台: {platform.system()} {platform.machine()}',
        ]
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            diag_lines.append(f'PyQt5 {QT_VERSION_STR}')
        except ImportError:
            diag_lines.append('❌ PyQt5 未安装')
        try:
            import requests
            diag_lines.append(f'requests {requests.__version__}')
        except ImportError:
            diag_lines.append('❌ requests 未安装')
        try:
            import psutil
            mem = psutil.virtual_memory()
            diag_lines.append(f'内存: {mem.used/(1024**3):.1f}/{mem.total/(1024**3):.0f} GB ({mem.percent}%)')
        except ImportError:
            diag_lines.append('❌ psutil 未安装')

        sn_key = self.app_settings.get('sensenova_api_key', '')
        ag_key = self.app_settings.get('agnes_api_key', '')
        if sn_key:
            diag_lines.append('AI: SenseNova ✓')
        elif ag_key:
            diag_lines.append('AI: Agnes ✓')
        else:
            diag_lines.append('AI: 未配置（使用本地报告）')

        QMessageBox.information(self, '环境诊断', '\n'.join(diag_lines))

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
        if getattr(sys, 'frozen', False):
            # PyInstaller 打包模式：直接运行 exe，不需要 pythonw.exe/.py
            return f'"{sys.executable}" --silent'
        # 开发模式：用 pythonw.exe 运行 .py（无控制台窗口）
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
            # Windows 10/11 还需要 StartupApproved\Run 条目，否则 Run 键值会被忽略
            approved_path = r'Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run'
            try:
                approved_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, approved_path, 0, winreg.KEY_SET_VALUE)
                if enabled:
                    # 02 00...00 = 启用
                    winreg.SetValueEx(approved_key, 'RestReminder', 0, winreg.REG_BINARY,
                                      b'\x02' + b'\x00' * 11)
                else:
                    try:
                        winreg.DeleteValue(approved_key, 'RestReminder')
                    except FileNotFoundError:
                        pass
                winreg.CloseKey(approved_key)
            except Exception as e2:
                log.warning(f'[自启动] StartupApproved 写入失败：{e2}')
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

    def _toast(self, title, message, icon_type=None, duration=3000):
        """统一通知入口：系统托盘 Toast（Win10/11 原生通知样式）"""
        if icon_type is None:
            icon_type = QSystemTrayIcon.Information
        if hasattr(self, 'tray_icon') and self.tray_icon:
            self.tray_icon.showMessage(title, message, icon_type, duration)

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
        """处理空闲状态 - 托盘提示 + popup 更新 + 清除浮球进度"""
        self._sync_buttons()
        self.tray_icon.setToolTip(f'⚡ 精力管理 · 续航 {self._activity_interval}min')
        if hasattr(self, 'floating_ball') and self.floating_ball._progress > 0:
            self.floating_ball.set_progress(0.0)

    def _handle_running(self, now):
        """处理运行状态 - 固定60分钟倒计时 -> 5分钟请辨 -> 5分钟休息"""
        # 浮球：确保清除环形进度
        if hasattr(self, 'floating_ball') and self.floating_ball._progress > 0:
            self.floating_ball.set_progress(0.0)

        elapsed = (now - self.start_time).total_seconds()
        total_seconds = self._activity_interval * 60  # 使用配置的间隔而非硬编码
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
            if self.app_settings.get('review_reminder', True):
                self._prompt_review()
            self._sync_buttons()
            log.info('[计时] 学习60分钟结束，进入5分钟休息')


    def _handle_resting(self, now):
        """处理休息状态 - 5分钟休息倒计时 + 累加休息时长 + 浮球环形进度"""
        if now >= self._rest_end_time:
            # 休息结束
            self._round_count += 1
            study_add = 1.0
            self.study_hours_today = round(self.study_hours_today + study_add, 2)
            self.update_study_display()
            LocalSync.increment_study_hour(self.study_hours_today)
            log.info(f'[计时] 休息结束，第{self._round_count}轮完成')
            self._check_achievements()

            # 浮球：恢复⚡图标，清除进度
            if hasattr(self, 'floating_ball'):
                self.floating_ball.set_progress(0.0)

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

            # 弹出本轮目标（非阻塞，60秒自动提交）
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
            # 累加休息时长（每秒 +1/60 分钟）
            self.break_minutes_today = round(self.break_minutes_today + 1/60, 2)

            # 浮球环形进度条：从 100% 到 0%
            remaining = (self._rest_end_time - now).total_seconds()
            rest_total = 5 * 60  # 5分钟 = 300秒
            progress = max(0.0, min(1.0, remaining / rest_total))
            if hasattr(self, 'floating_ball'):
                self.floating_ball.set_progress(progress)

            # 显示休息倒计时（通过 popup）
            self._sync_buttons()
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            self.tray_icon.setToolTip(f'⚡ 精力管理 · 休息中 {mins}:{secs:02d}')

    def _handle_paused(self, now):
        """处理暂停状态 - 托盘提示 + popup 更新 + 清除浮球进度"""
        self._sync_buttons()
        self.tray_icon.setToolTip('⚡ 精力管理 · ⏸ 已暂停')
        if hasattr(self, 'floating_ball') and self.floating_ball._progress > 0:
            self.floating_ball.set_progress(0.0)
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
            # 窗口浮现到前台
            if self.isMinimized() or not self.isVisible():
                self.show()
                self.raise_()
                self.activateWindow()
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
                remaining_secs = 22 * 3600 - seconds_since_midnight
                h = int(remaining_secs // 3600)
                m = int((remaining_secs % 3600) // 60)
                lbl.setText(f'剩余 {h}小时{m}分钟')
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

            # --- 20-20-20 护眼提醒（每20分钟一次，学习状态时触发） ---
            if self.timer_state == 'running':
                if self._last_eye_rest_time is None:
                    self._last_eye_rest_time = now
                elif (now - self._last_eye_rest_time).total_seconds() >= 1200:
                    self.eye_rest_overlay.show_reminder()
                    self._last_eye_rest_time = now
            else:
                # 非学习状态时重置计时器，避免休息时也算时间
                self._last_eye_rest_time = None

            # --- 22:00 倒计时（统一更新，避免重复请求） ---
            self._update_countdown(now)
            self._update_countdown_display()

            # --- 刷新今日 tab 动态内容 ---
            self._refresh_general_tab()

            # --- 每 60 秒检查周报 ---
            if not hasattr(self, '_weekly_check_tick'):
                self._weekly_check_tick = 0
            self._weekly_check_tick += 1
            if self._weekly_check_tick >= 60:
                self._weekly_check_tick = 0
                self._check_weekly_report()

            # --- 每 15 秒电池检测 ---
            self._battery_tick += 1
            if self._battery_tick >= 15:
                self._battery_tick = 0
                self.update_battery_status()

            # --- 每5分钟保存历史统计 ---
            self._stats_tick += 1
            if self._stats_tick >= 300:
                self._stats_tick = 0
                LocalSync.save_daily_stats(rounds=self._round_count)

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
        """每秒刷新今日 tab 中的动态元素（数据卡片 + 状态 + 倒计时 + 休息时长）"""
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
                bc._value_label.setText(f'{self.break_minutes_today:.1f} 分钟')

            # 状态标签 + 计时器标签
            state_lbl = refs.get('state_lbl')
            if state_lbl and not sip.isdeleted(state_lbl):
                state_names = {'idle': '⏸ 待机', 'running': '▶ 学习中', 'resting': '☕ 休息中', 'paused': '⏸ 已暂停'}
                state_lbl.setText(f'状态：{state_names.get(self.timer_state, self.timer_state)}')

            # 计时器标签（本轮剩余/休息剩余）
            timer_lbl = refs.get('timer_lbl')
            if timer_lbl and not sip.isdeleted(timer_lbl):
                if self.timer_state == 'running' and self.start_time:
                    elapsed = (datetime.now() - self.start_time).total_seconds() / 60
                    remaining = max(0, 60 - elapsed)
                    timer_lbl.setText(f'⏱ 本轮剩余：{remaining:.0f} 分钟')
                    timer_lbl.setStyleSheet('color: #6a8cbb; font-size: 12px;')
                elif self.timer_state == 'resting' and self._rest_end_time:
                    remaining = max(0, (self._rest_end_time - datetime.now()).total_seconds() / 60)
                    timer_lbl.setText(f'⏱ 休息剩余：{remaining:.0f} 分钟')
                    timer_lbl.setStyleSheet('color: #d97757; font-size: 12px;')
                elif self.timer_state == 'paused' and self.remaining_when_paused:
                    remaining = max(0, self.remaining_when_paused / 60)
                    timer_lbl.setText(f'⏱ 暂停剩余：{remaining:.0f} 分钟')
                    timer_lbl.setStyleSheet('color: #888; font-size: 12px;')
            # ── 日程卡片刷新 ──
            if self._calendar_enabled:
                self._refresh_calendar_display()

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
        subject_val = [self.app_settings.get('last_review_subject', '未记录')]
        for subj in _SUBJECTS:
            btn = QPushButton(subj)
            btn.setCheckable(True)
            btn.setFixedSize(56, 36)
            # 记忆上次选择
            if subj == subject_val[0]:
                btn.setChecked(True)
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
        label_val = [self.app_settings.get('last_review_label', '未记录')]
        for lbl in _LABELS:
            btn = QPushButton(lbl)
            btn.setCheckable(True)
            btn.setFixedSize(56, 36)
            # 记忆上次选择
            if lbl == label_val[0]:
                btn.setChecked(True)
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
        if dialog.exec_():
            subject = dialog._subject_val[0]
            label = dialog._label_val[0]
            score = dialog._score_slider.value()
            self._write_review(score, subject, label)
            self.tray_icon.showMessage('📝 已补录', f'{score}分 | {subject} | {label}', QSystemTrayIcon.Information, 2000)

    def _write_review(self, score, subject='未记录', label='未记录'):
        """写入复盘记录到文件（供正常复盘和补录共用）"""
        try:
            # 记忆学科和标签，下次复盘自动选中
            if subject != '未记录':
                self.app_settings['last_review_subject'] = subject
            if label != '未记录':
                self.app_settings['last_review_label'] = label
            LocalSync.save_settings(self.app_settings)

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

    def _show_onboarding(self):
        """首次引导：3页弹窗介绍核心功能"""
        dialog = QDialog(self)
        dialog.setWindowTitle('欢迎使用休息提醒')
        dialog.setFixedSize(480, 360)
        dialog.setStyleSheet("""
            QDialog { background-color: #18181f; border-radius: 16px; }
            QLabel { color: #e8e4dc; font-size: 14px; background: transparent; }
            QLabel#title { font-size: 20px; font-weight: bold; color: #d4a853; }
            QLabel#emoji { font-size: 48px; background: transparent; }
            QPushButton {
                background: rgba(212,168,83,0.12); color: #d4a853;
                border: 1px solid rgba(212,168,83,0.25); border-radius: 10px;
                padding: 10px 24px; font-size: 14px; font-weight: bold;
            }
            QPushButton:hover { background: rgba(212,168,83,0.20); }
        """)

        pages = [
            {
                'emoji': '⏰',
                'title': '浮球操作',
                'desc': '屏幕右侧的浮球是你的快捷入口\n• 单击打开主界面\n• 拖动改变位置\n• 右键打开菜单'
            },
            {
                'emoji': '⚡',
                'title': '60 + 5 分钟循环',
                'desc': '专注学习的固定节奏\n• 学习 60 分钟 → 倒计时浮层提醒\n• 复盘 1-100 分 → 5 分钟休息\n• 打开 B 站收藏夹放松\n• 自动进入下一轮'
            },
            {
                'emoji': '🤖',
                'title': 'AI 复盘与报告',
                'desc': '每轮结束复盘学习质量\n• 学科 + 标签 + 1-100 分评分\n• AI 自动分析学习趋势\n• 每周一早 8 点邮件推送周报'
            },
        ]

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(30, 30, 30, 20)
        layout.setSpacing(15)

        emoji_lbl = QLabel()
        emoji_lbl.setObjectName('emoji')
        emoji_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(emoji_lbl)

        title_lbl = QLabel()
        title_lbl.setObjectName('title')
        title_lbl.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_lbl)

        desc_lbl = QLabel()
        desc_lbl.setAlignment(Qt.AlignCenter)
        desc_lbl.setWordWrap(True)
        layout.addWidget(desc_lbl)

        layout.addStretch()

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        skip_btn = QPushButton('跳过')
        skip_btn.clicked.connect(dialog.reject)
        next_btn = QPushButton('下一步')
        next_btn.setObjectName('accentBtn')
        btn_layout.addStretch()
        btn_layout.addWidget(skip_btn)
        btn_layout.addWidget(next_btn)
        layout.addLayout(btn_layout)

        idx = [0]
        def show_page():
            pg = pages[idx[0]]
            emoji_lbl.setText(pg['emoji'])
            title_lbl.setText(pg['title'])
            desc_lbl.setText(pg['desc'])
            if idx[0] == len(pages) - 1:
                next_btn.setText('开始使用')
            else:
                next_btn.setText('下一步')

        def on_next():
            if idx[0] < len(pages) - 1:
                idx[0] += 1
                show_page()
            else:
                dialog.accept()

        next_btn.clicked.connect(on_next)
        show_page()

        if dialog.exec_() == QDialog.Accepted:
            self.app_settings['onboarding_shown'] = True
            LocalSync.save_settings(self.app_settings)
            # 引导结束后提示设目标
            self._prompt_goal()
        else:
            # 跳过也标记为已展示
            self.app_settings['onboarding_shown'] = True
            LocalSync.save_settings(self.app_settings)
            self._prompt_goal()

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
        # 恢复状态后检查连续打卡（跨重启 streak 不丢失）
        self._check_streak()
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

    def _get_achievement_stats(self):
        """获取每个成就的当前进度信息"""
        stats = {}
        try:
            history = history_store.load()
            total_study = sum(v.get('study', 0) for v in history.values())
            total_rounds = sum(v.get('rounds', 0) for v in history.values())
            # 本周学习时长（最近 7 天）
            now = datetime.now()
            week_ago = (now - timedelta(days=7)).date().isoformat()
            week_study = sum(v.get('study', 0) for d, v in history.items() if d >= week_ago)
            # 本月学习时长（当月）
            month_prefix = now.strftime('%Y-%m')
            month_study = sum(v.get('study', 0) for d, v in history.items() if d.startswith(month_prefix))
            reviews = review_store.load()
            total_reviews = sum(len(v) for v in reviews.values())
            max_score = 0
            for day_reviews in reviews.values():
                for r in day_reviews:
                    s = r.get('score', 0)
                    if s > max_score:
                        max_score = s
            streak = LocalSync.load_streak()
            today_study = self.study_hours_today

            # 每个成就的进度文本
            thresholds = {
                'first_hour': (total_study, 1, 'h'),
                'ten_hours': (total_study, 10, 'h'),
                'fifty_hours': (total_study, 50, 'h'),
                'hundred_hours': (total_study, 100, 'h'),
                'week_30h': (week_study, 30, 'h'),
                'month_100h': (month_study, 100, 'h'),
                'streak_3': (streak.get('current_streak', 0), 3, '天'),
                'streak_7': (streak.get('current_streak', 0), 7, '天'),
                'streak_14': (streak.get('current_streak', 0), 14, '天'),
                'streak_30': (streak.get('current_streak', 0), 30, '天'),
                'daily_4h': (today_study, 4, 'h'),
                'daily_8h': (today_study, 8, 'h'),
                'review_10': (total_reviews, 10, '次'),
                'review_50': (total_reviews, 50, '次'),
                'review_100': (total_reviews, 100, '次'),
                'perfect_score': (max_score, 100, '分'),
                'rounds_10': (total_rounds, 10, '轮'),
                'rounds_50': (total_rounds, 50, '轮'),
                'rounds_100': (total_rounds, 100, '轮'),
            }
            for ach_id, (current, target, unit) in thresholds.items():
                pct = min(current / max(target, 1), 1.0)
                stats[ach_id] = {
                    'current': current,
                    'target': target,
                    'unit': unit,
                    'pct': pct,
                    'progress_text': f'{current}/{target}{unit} ({int(pct*100)}%)'
                }
        except Exception as e:
            log.warning(f'[成就] 获取进度失败: {e}')
        return stats

    def _check_achievements(self, silent=False):
        """检查并解锁成就。silent=True 时不弹 Toast（启动时用）。"""
        try:
            data = achievements_store.load()
            earned = data.get('earned', {})

            # 构建检查数据
            history = history_store.load()
            total_study = sum(v.get('study', 0) for v in history.values())
            total_rounds = sum(v.get('rounds', 0) for v in history.values())
            # 本周学习时长（最近 7 天）
            now = datetime.now()
            week_ago = (now - timedelta(days=7)).date().isoformat()
            week_study = sum(v.get('study', 0) for d, v in history.items() if d >= week_ago)
            # 本月学习时长（当月）
            month_prefix = now.strftime('%Y-%m')
            month_study = sum(v.get('study', 0) for d, v in history.items() if d.startswith(month_prefix))
            reviews = review_store.load()
            total_reviews = sum(len(v) for v in reviews.values())
            max_score = 0
            for day_reviews in reviews.values():
                for r in day_reviews:
                    s = r.get('score', 0)
                    if s > max_score:
                        max_score = s
            streak = LocalSync.load_streak()

            check_data = {
                'total_study': total_study,
                'total_rounds': total_rounds,
                'total_reviews': total_reviews,
                'max_score': max_score,
                'current_streak': streak.get('current_streak', 0),
                'today_study': self.study_hours_today,
                'week_study': week_study,
                'month_study': month_study,
            }

            new_achievements = []
            for ach in _ACHIEVEMENTS:
                if ach['id'] not in earned:
                    try:
                        if ach['check'](check_data):
                            earned[ach['id']] = datetime.now().isoformat()
                            new_achievements.append(ach)
                    except Exception:
                        pass

            if new_achievements:
                achievements_store.save({'earned': earned})
                for ach in new_achievements:
                    if not silent:
                        self._toast(f'{ach["icon"]} 成就解锁：{ach["name"]}', ach['desc'], duration=8000)
                    log.info(f'[成就] 解锁: {ach["id"]} - {ach["name"]}{" (静默)" if silent else ""}')
        except Exception as e:
            log.warning(f'[成就] 检查失败: {e}')

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
            if event.buttons() == Qt.LeftButton and self.drag_position is not None:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
        except Exception as e:
            log.error(f'[mouseMoveEvent 异常] {type(e).__name__}: {e}')

    def hideEvent(self, event):
        super().hideEvent(event)

    def closeEvent(self, event):
        # 停止环境音
        if hasattr(self, '_ambient_player'):
            self._ambient_player.stop()
        # 停止飞书日程管理器
        if hasattr(self, "_calendar_mgr"):
            self._calendar_mgr.stop()

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
            if hasattr(self, 'eye_rest_overlay'):
                self.eye_rest_overlay.hide_overlay()
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

    # 全局图标：QApplication 级别设置，影响任务栏/Alt-Tab
    app_icon = _create_app_icon()
    app.setWindowIcon(app_icon)

    # Windows 任务栏分组图标：设置 AppUserModelID，避免被识别为 python.exe
    # 这样任务栏会显示应用图标而不是 Python 默认图标
    try:
        app_id = 'CrazyStudio.RestReminder'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        log.warning('[任务栏] 设置 AppUserModelID 失败')

    silent = '--silent' in sys.argv
    widget = RestReminderWidget(silent_start=silent)
    if silent:
        widget.hide()
    else:
        widget.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
