"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
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
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox, QShortcut)
from PyQt5.QtCore import QTimer, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon, QFont, QCursor, QPainter, QColor, QBrush, QPen, QKeySequence
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
        self.interval_minutes = 60
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
        # 启动时先显示主窗口看看效果
        self.show()
        # 移到屏幕右侧
        screen = QApplication.primaryScreen()
        if screen:
            screen_geom = screen.geometry()
            self.move(screen_geom.width() - 400, screen_geom.height() // 2 - 200)
        # 恢复上次运行状态（跨重启续接）
        self._restore_active_state()

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
                background-color: #0a0a0c;
                border-radius: 20px;
                color: #e8e6e1;
            }
            QWidget#mainWindow {
                background: qradialgradient(cx:0.5, cy:0.0, radius:0.8,
                    stop:0 rgba(212, 175, 55, 0.04), stop:1 #0a0a0c);
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
            }
            QPushButton#closeBtn:hover {
                color: #d4af37;
            }
            QProgressBar {
                border: none;
                border-radius: 3px;
                background-color: #1a1918;
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

        self.title_label = QLabel('⏰ 休息提醒')
        self.title_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 12, QFont.Bold))
        self.title_label.setStyleSheet('color: #d4af37;')
        top_layout.addWidget(self.title_label)
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

        self.time_label = QLabel('60:00')
        self.time_label.setFont(QFont('Consolas, "SF Mono", monospace', 56, QFont.Bold))
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet('color: #d4af37; letter-spacing: 4px;')
        main_layout.addWidget(self.time_label)

        time_hint = QLabel('距离下次休息')
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
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(212, 175, 55, 0.12);
                color: #d4af37;
                border: 1.5px solid rgba(212, 175, 55, 0.4);
                border-radius: 20px;
                padding: 0 28px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(212, 175, 55, 0.22);
                border-color: #d4af37;
            }
        """)
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton('⏸ 暂停')
        self.pause_btn.setFont(QFont('Georgia, "Noto Serif SC", serif', 11, QFont.Bold))
        self.pause_btn.setFixedHeight(40)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(212, 175, 55, 0.12);
                color: #d4af37;
                border: 1.5px solid rgba(212, 175, 55, 0.4);
                border-radius: 20px;
                padding: 0 28px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: rgba(212, 175, 55, 0.22);
                border-color: #d4af37;
            }
            QPushButton:disabled {
                background-color: transparent;
                color: #3a3835;
                border-color: #2a2928;
            }
        """)
        self.pause_btn.clicked.connect(self.on_pause_clicked)
        btn_layout.addWidget(self.pause_btn)
        main_layout.addLayout(btn_layout)

        # ═══ 分隔线 ═══
        main_layout.addSpacing(24)

        sep = QLabel()
        sep.setFixedHeight(1)
        sep.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.15 #2a2928, stop:0.85 #2a2928, stop:1 transparent);')
        main_layout.addWidget(sep)

        # ═══ 二级信息区：卡片式分组 ═══
        main_layout.addSpacing(16)

        # 第一行：学习时长 + 打卡
        row1 = QHBoxLayout()
        row1.setSpacing(12)

        study_card = QVBoxLayout()
        study_card.setSpacing(2)
        self.study_progress_label = QLabel('📚 学习 0h')
        self.study_progress_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 10))
        self.study_progress_label.setStyleSheet('color: #d4af37;')
        study_card.addWidget(self.study_progress_label)

        self.study_progress_bar = QProgressBar()
        self.study_progress_bar.setObjectName('study_bar')
        self.study_progress_bar.setMaximum(14)
        self.study_progress_bar.setValue(0)
        self.study_progress_bar.setTextVisible(False)
        self.study_progress_bar.setFixedHeight(4)
        self.study_progress_bar.setStyleSheet("""
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #8b6914, stop:0.5 #d4af37, stop:1 #f0d060); }
        """)
        study_card.addWidget(self.study_progress_bar)
        row1.addLayout(study_card)

        streak = self.streak_data
        streak_text = f'🔥 {streak["current_streak"]}天' if streak['current_streak'] > 0 else '🔥 0天'
        self.streak_label = QLabel(streak_text)
        self.streak_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 10))
        self.streak_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.streak_label.setStyleSheet('color: #d97757;')
        row1.addWidget(self.streak_label)
        main_layout.addLayout(row1)

        main_layout.addSpacing(12)

        # 第二行：22:00倒计时 + 休息时长
        row2 = QHBoxLayout()
        row2.setSpacing(12)

        self.countdown_label = QLabel('⏳ 22:00')
        self.countdown_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 10))
        self.countdown_label.setStyleSheet('color: #6a9bcc;')
        row2.addWidget(self.countdown_label)

        self.break_label = QLabel('☕ --')
        self.break_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 10))
        self.break_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.break_label.setStyleSheet('color: #8b6914;')
        row2.addWidget(self.break_label)
        main_layout.addLayout(row2)

        self.countdown_bar = QProgressBar()
        self.countdown_bar.setObjectName('countdown_bar')
        self.countdown_bar.setMaximum(100)
        self.countdown_bar.setValue(100)
        self.countdown_bar.setTextVisible(False)
        self.countdown_bar.setFixedHeight(3)
        self.countdown_bar.setStyleSheet("""
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2a5a8a, stop:0.5 #6a9bcc, stop:1 #8ab8e0); }
        """)
        main_layout.addWidget(self.countdown_bar)

        # ═══ 底部：电脑使用 + 电池 ═══
        main_layout.addSpacing(16)

        row3 = QHBoxLayout()
        row3.setSpacing(12)

        self.computer_usage_label = QLabel('💻 0H00min')
        self.computer_usage_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.computer_usage_label.setStyleSheet('color: #7a5aab;')
        row3.addWidget(self.computer_usage_label)

        self.battery_label = QLabel('🔋 检测中')
        self.battery_label.setFont(QFont('Georgia, "Noto Serif SC", serif', 9))
        self.battery_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.battery_label.setStyleSheet('color: #5a8a30;')
        row3.addWidget(self.battery_label)
        main_layout.addLayout(row3)

        self.computer_usage_bar = QProgressBar()
        self.computer_usage_bar.setObjectName('computer_usage_bar')
        self.computer_usage_bar.setMaximum(100)
        self.computer_usage_bar.setValue(100)
        self.computer_usage_bar.setTextVisible(False)
        self.computer_usage_bar.setFixedHeight(3)
        self.computer_usage_bar.setStyleSheet("""
            QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a2a7a, stop:0.5 #7a5aab, stop:1 #9b6acc); }
        """)
        main_layout.addWidget(self.computer_usage_bar)

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

        stats_action = QAction('📊 学习统计', self)
        stats_action.triggered.connect(self.show_stats)
        tray_menu.addAction(stats_action)

        # --- 连续打卡显示 ---
        streak = self.streak_data
        if streak['current_streak'] > 0:
            streak_action = QAction(f'🔥 连续打卡 {streak["current_streak"]} 天', self)
        else:
            streak_action = QAction('🔥 连续打卡 0 天', self)
        streak_action.setEnabled(False)  # 只显示，不可点击
        tray_menu.addAction(streak_action)

        # --- 提醒方式子菜单 ---
        reminder_menu = tray_menu.addMenu('🔔 提醒方式')
        self._reminder_actions = {}
        current_mode = self.app_settings.get('reminder_mode', 'video')
        mode_options = [
            ('video', '打开B站'),
            ('notify', '只弹通知'),
            ('none', '无操作'),
        ]
        for mode_key, mode_label in mode_options:
            action = QAction(mode_label, self)
            action.setCheckable(True)
            action.setChecked(mode_key == current_mode)
            action.triggered.connect(lambda checked, k=mode_key: self._set_reminder_mode(k))
            reminder_menu.addAction(action)
            self._reminder_actions[mode_key] = action

        # --- 导出本周数据 ---
        export_action = QAction('📋 导出本周数据', self)
        export_action.triggered.connect(self.export_weekly_data)
        tray_menu.addAction(export_action)

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

    def _pause_timer(self):
        """暂停计时器（计算剩余时间）"""
        remaining = self.interval_minutes * 60 - (datetime.now() - self.start_time).total_seconds()
        self.remaining_when_paused = max(remaining, 0)
        self.timer_state = 'paused'
        self._sync_buttons()

    def _resume_timer(self):
        """恢复计时器（从暂停位置继续）"""
        if self.remaining_when_paused is None:
            log.warning('[_resume_timer] remaining_when_paused is None, resetting to idle')
            self._reset_timer_to_idle()
            return
        self.start_time = datetime.now() - timedelta(seconds=(self.interval_minutes * 60 - self.remaining_when_paused))
        self.remaining_when_paused = None
        self.timer_state = 'running'
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
        """处理空闲状态 - 显示默认时间"""
        self.time_label.setText(f'距离下次休息：{self.interval_minutes:02d}:00')
        self.progress_bar.setValue(0)
        # 如果有 break_start，实时更新休息时长显示
        if self.break_start is not None:
            self._update_break_display()

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
                random.choice([
                    '还剩不到5分钟，准备休息一下~',
                    '快到休息时间了，站起来活动活动~',
                    '还有一小会儿，准备喝口水~',
                    '即将休息，眼睛可以放松一下了~',
                ]),
                total_seconds=300
            )
        # 倒计时结束（包含浮层清理）
        if remaining <= 0:
            self._study_countdown_active = False
            # 不直接隐藏浮层：电脑使用倒计时可能还在运行
            if not self._computer_countdown_active:
                self.countdown_overlay.hide_overlay()
            # 记录休息开始时间（用于追踪休息时长）
            self.break_start = datetime.now()
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
            else:  # 'none'
                log.info('[提醒方式] 无操作模式，不弹通知不打开视频')
            self.study_hours_today += 1
            self.update_study_display()
            LocalSync.increment_study_hour(self.study_hours_today)
            self._reset_timer_to_idle()

    def _handle_paused(self, now):
        """处理暂停状态 - 显示暂停时间"""
        if self.remaining_when_paused is None:
            self.time_label.setText('⏸ 已暂停')
            return
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
                self.computer_3h_cycles_today = 0
                self.computer_usage_reminder_given_at = None
                self._study_countdown_active = False
                self._computer_countdown_active = False
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
        """更新学习时长显示"""
        h = self.study_hours_today
        self.study_progress_label.setText(f'📚 学习时长：{h}小时')
        self.study_progress_bar.setValue(h)

    def _update_break_display(self):
        """更新休息时长显示"""
        if self.break_start is not None:
            # 正在休息中，实时显示
            elapsed = (datetime.now() - self.break_start).total_seconds() / 60
            self.break_label.setText(f'☕ 本次休息：{elapsed:.0f}分钟')
        elif self.break_minutes_today > 0:
            self.break_label.setText(f'☕ 今日休息：{self.break_minutes_today:.0f}分钟')
        else:
            self.break_label.setText('☕ 今日休息：0分钟')

    def _set_reminder_mode(self, mode):
        """设置提醒方式"""
        self.app_settings['reminder_mode'] = mode
        LocalSync.save_settings(self.app_settings)
        # 更新菜单勾选状态
        for key, action in self._reminder_actions.items():
            action.setChecked(key == mode)
        mode_names = {'video': '打开B站', 'notify': '只弹通知', 'none': '无操作'}
        self.tray_icon.showMessage('提醒方式', f'已切换为：{mode_names.get(mode, mode)}', QSystemTrayIcon.Information, 2000)
        log.info(f'[设置] 提醒方式切换为: {mode}')

    def _restore_active_state(self):
        """启动时恢复上次运行状态（跨重启续接）"""
        state = LocalSync.load_app_state()
        if state is None:
            return

        # 休息时长：app_state 是绝对值（最新），优先于 daily_log
        self.break_minutes_today = state.get('break_minutes', self.break_minutes_today)

        # 计时器状态恢复
        saved_state = state.get('timer_state')
        if saved_state == 'running':
            saved_remaining = state.get('remaining', 0)
            if saved_remaining > 0 and saved_remaining < self.interval_minutes * 60:
                self.start_time = datetime.now() - timedelta(seconds=(self.interval_minutes * 60 - saved_remaining))
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
        self.update_study_display()
        self._update_break_display()

    def _save_active_state(self):
        """保存当前运行状态到本地文件（防崩溃丢失）"""
        remaining = 0
        if self.timer_state == 'running' and self.start_time:
            remaining = max(self.interval_minutes * 60 - (datetime.now() - self.start_time).total_seconds(), 0)
        elif self.timer_state == 'paused' and self.remaining_when_paused is not None:
            remaining = self.remaining_when_paused

        state = {
            'timer_state': self.timer_state,
            'remaining': round(remaining),
            'break_start': self.break_start.isoformat() if self.break_start else None,
            'break_minutes': self.break_minutes_today,
            'played_today': list(self.played_today),
        }
        LocalSync.save_app_state(state)

    def _check_streak(self):
        """检查连续打卡：学习时长>=4小时则打卡"""
        today = datetime.now().date().isoformat()
        streak = self.streak_data
        if self.study_hours_today >= 4:
            if streak.get('last_streak_date') != today:
                streak['current_streak'] = streak.get('current_streak', 0) + 1
                streak['last_streak_date'] = today
                if streak['current_streak'] > streak.get('best_streak', 0):
                    streak['best_streak'] = streak['current_streak']
                log.info(f'[打卡] 今日学习{self.study_hours_today}h >= 4h，连续打卡 {streak["current_streak"]} 天')
        else:
            if streak.get('last_streak_date') != today:
                streak['current_streak'] = 0
                log.info(f'[打卡] 今日学习{self.study_hours_today}h < 4h，打卡中断')
        self.streak_data = streak
        LocalSync.save_streak(streak)
        self._update_streak_display()

    def _update_streak_display(self):
        """更新连续打卡显示"""
        streak = self.streak_data
        if streak['current_streak'] > 0:
            self.streak_label.setText(f'🔥 连续打卡：{streak["current_streak"]}天（最佳{streak["best_streak"]}天）')
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
        """获取 B 站收藏夹视频列表（带重试）"""
        import re as _re  # 模块级 re 在 daemon 线程中偶尔不可用，本地导入兜底
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
                        if bvid and _re.match(r'^BV[a-zA-Z0-9]{10}$', bvid):
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
