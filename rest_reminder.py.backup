"""
桌面休息提醒挂件
- 每小时提醒休息，并随机打开 B 站收藏夹中的视频
- 监控电池充电状态
- 监控电脑使用时长（每 3 小时提醒）
- 学习时长本地计数（每次倒计时完成算 1 小时）
- 飞书每日数据记录：电脑使用时长、学习时长、电脑故障率
"""
import sys
import time
import random
import requests
import ctypes
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QTimer, Qt, QPoint
from PyQt5.QtGui import QIcon, QFont, QCursor, QPainter, QColor, QBrush, QPen
import psutil
import os
import tempfile
import atexit
import winreg
import traceback


def open_url(url):
    """使用 Windows API 打开 URL，避免弹出命令窗口"""
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
        print(f'[open_url] 使用 ShellExecuteW 失败: {e}')
        try:
            import webbrowser
            return webbrowser.open(url)
        except Exception as e2:
            print(f'[open_url] 使用 webbrowser 也失败: {e2}')
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


class AudioDeviceDetector:
    """音频设备检测器 - 检测麦克风/扬声器是否可用"""
    def __init__(self):
        self._known_devices = {}
        self._check_interval = 300
        self._check_counter = 0
        self._on_device_failed = None
        self._device_failure_reported = set()

    def set_failure_callback(self, callback):
        """设置设备故障回调"""
        self._on_device_failed = callback

    def check_devices(self):
        """检测音频设备状态（简化版）"""
        try:
            import subprocess
            result = subprocess.run(
                ['powershell', '-Command',
                 'Get-WmiObject -Class Win32_SoundDevice | Select-Object Name, Status'],
                capture_output=True,
                text=True,
                timeout=3
            )

            if result.returncode != 0:
                return None

            output = result.stdout.strip()

            # 简单检查：如果输出中没有 "OK" 或者为空，可能有问题
            if output and 'OK' in output:
                # 打印发现的设备
                print(f'[AudioDeviceDetector] 音频设备状态正常')
                return True

            return None

        except Exception as e:
            print(f'[AudioDeviceDetector] 检测跳过: {e}')
            return None

    def tick(self):
        """定时检测（每次调用计数，达到间隔才检测）"""
        self._check_counter += 1
        if self._check_counter >= self._check_interval:
            self._check_counter = 0
            return self.check_devices()
        return None


# 飞书配置
FEISHU_WIKI_TOKEN = 'NO0IwcUKFis5L2kOyMDcHOd1nId'  # 飞书知识库 token
FEISHU_BASE_TOKEN = 'DcJzbLadCaGbGws2ZekchGHhnVe'  # 飞书多维表格 token
FEISHU_TABLE_ID = 'tbl9DT9qniE63BH7'  # 【新】每日追踪 表的 ID
FEISHU_TABLE_NAME = '每日追踪'
# lark-cli 路径配置
LARK_CLI_NODE_PATH = r"C:\Program Files\nodejs\node.exe"
LARK_CLI_PATH = r"C:\Users\binlo\AppData\Roaming\npm\node_modules\@larksuite\cli\scripts\run.js"


class FeishuDailyTracker:
    """飞书每日数据追踪器"""
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = data_dir
        self.state_file = os.path.join(data_dir, 'daily_tracker_state.json')
        self.crash_log_file = os.path.join(data_dir, 'crash.log')
        self._load_state()

    def _load_state(self):
        """加载状态"""
        try:
            if os.path.exists(self.state_file):
                with open(self.state_file, 'r', encoding='utf-8') as f:
                    self.state = json.load(f)
            else:
                self.state = {
                    'current_date': datetime.now().date().isoformat(),
                    'device_failure_count_today': 0,
                    'last_recorded_date': None,
                    'last_synced_to_feishu_date': None  # 新增：记录最后同步到飞书的日期
                }
        except Exception:
            self.state = {
                'current_date': datetime.now().date().isoformat(),
                'device_failure_count_today': 0,
                'last_recorded_date': None,
                'last_synced_to_feishu_date': None
            }

    def _save_state(self):
        """保存状态"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(self.state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f'[FeishuDailyTracker] 保存状态失败: {e}')

    def check_date_change(self):
        """检查日期变化，返回 True 如果是新的一天"""
        today = datetime.now().date().isoformat()
        if self.state['current_date'] != today:
            # 新的一天
            self.state['last_recorded_date'] = self.state['current_date']
            self.state['current_date'] = today
            self.state['crash_count_today'] = 0
            self._save_state()
            return True
        return False

    def record_device_failure(self):
        """记录音频设备故障"""
        self.state['device_failure_count_today'] = self.state.get('device_failure_count_today', 0) + 1
        self._save_state()

    def get_device_failure_count_today(self):
        """获取今天设备故障次数"""
        return self.state.get('device_failure_count_today', 0)

    def _sync_to_feishu_via_cli(self, record):
        """通过 lark-cli 同步数据到飞书多维表格"""
        try:
            if not os.path.exists(LARK_CLI_NODE_PATH) or not os.path.exists(LARK_CLI_PATH):
                print(f'[FeishuDailyTracker] lark-cli 未找到，跳过飞书同步')
                return False

            # 先查询是否已存在该日期的记录
            date_str = record['date']
            query_cmd = [
                LARK_CLI_NODE_PATH, LARK_CLI_PATH,
                "base", "+record-list",
                "--base-token", FEISHU_BASE_TOKEN,
                "--table-id", FEISHU_TABLE_ID,
                "--filter", f'日期 = "{date_str}"',
                "--as", "user"
            ]

            import subprocess
            result = subprocess.run(query_cmd, capture_output=True, text=True, encoding='utf-8', timeout=30)
            
            existing_record_id = None
            if result.returncode == 0 and result.stdout:
                try:
                    output_json = json.loads(result.stdout)
                    if output_json.get('data', {}).get('items'):
                        existing_record_id = output_json['data']['items'][0].get('record_id')
                except:
                    pass

            # 准备记录数据
            fields = {
                "日期": date_str,
                "学习时长": round(record['study_hours'], 1),
                "电脑使用时长": round(record['computer_usage_hours'], 1),
                "电脑故障率": round(record['failure_rate'], 2),
                "崩溃次数": record.get('crash_count', 0),
                "设备故障次数": record.get('device_failure_count', 0)
            }

            if existing_record_id:
                # 更新现有记录
                cmd = [
                    LARK_CLI_NODE_PATH, LARK_CLI_PATH,
                    "base", "+record-update",
                    "--base-token", FEISHU_BASE_TOKEN,
                    "--table-id", FEISHU_TABLE_ID,
                    "--record-id", existing_record_id,
                    "--json", json.dumps({"fields": fields}, ensure_ascii=False),
                    "--as", "user"
                ]
                action = "更新"
            else:
                # 创建新记录
                cmd = [
                    LARK_CLI_NODE_PATH, LARK_CLI_PATH,
                    "base", "+record-create",
                    "--base-token", FEISHU_BASE_TOKEN,
                    "--table-id", FEISHU_TABLE_ID,
                    "--json", json.dumps({"fields": fields}, ensure_ascii=False),
                    "--as", "user"
                ]
                action = "创建"

            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=30)
            
            if result.returncode == 0:
                print(f'[FeishuDailyTracker] 飞书{action}成功: {date_str}')
                self.state['last_synced_to_feishu_date'] = date_str
                self._save_state()
                return True
            else:
                print(f'[FeishuDailyTracker] 飞书{action}失败: {result.stderr}')
                return False

        except Exception as e:
            print(f'[FeishuDailyTracker] 飞书同步异常: {e}')
            import traceback
            traceback.print_exc()
            return False

    def sync_to_feishu(self, study_hours, computer_usage_hours, force_sync=False):
        """同步数据到飞书"""
        record = {
            'date': datetime.now().date().isoformat(),
            'study_hours': study_hours,
            'computer_usage_hours': computer_usage_hours,
            'device_failure_count': self.get_device_failure_count_today(),
            'crash_count': self.state.get('crash_count_today', 0),
            'failure_rate': self._calculate_failure_rate(computer_usage_hours),
            'recorded_at': datetime.now().isoformat()
        }

        # 先保存到本地
        records_file = os.path.join(self.data_dir, 'daily_records.json')
        try:
            records = []
            if os.path.exists(records_file):
                with open(records_file, 'r', encoding='utf-8') as f:
                    records = json.load(f)

            updated = False
            for i, r in enumerate(records):
                if r.get('date') == record['date']:
                    records[i] = record
                    updated = True
                    break
            if not updated:
                records.append(record)

            with open(records_file, 'w', encoding='utf-8') as f:
                json.dump(records, f, ensure_ascii=False, indent=2)

            print(f'[FeishuDailyTracker] 数据已记录到本地: {record}')
        except Exception as e:
            print(f'[FeishuDailyTracker] 记录本地数据失败: {e}')

        # 同步到飞书
        self._sync_to_feishu_via_cli(record)

    def _calculate_failure_rate(self, computer_usage_hours):
        """计算故障率（每小时设备故障次数）"""
        if computer_usage_hours < 0.1:
            return 0.0
        return self.get_device_failure_count_today() / computer_usage_hours

    def record_crash(self):
        """记录崩溃（保持向后兼容）"""
        self.state['crash_count_today'] = self.state.get('crash_count_today', 0) + 1
        self._save_state()


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
            print(f'单实例检查失败：{e}')
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
            print(f'备用单实例检查失败：{e}')
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
            print(f'[VideoFetchThread] 获取视频异常：{e}')
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

        # 电脑使用时长监控（每 3 小时提醒一次）
        self.computer_usage_hours_today = 0
        self.last_computer_usage_check = datetime.now()
        self.computer_usage_reminder_given_at = None  # 记录上次提醒的时间点（小时数）

        # 天气刷新计数器（每 30 分钟）
        self._weather_tick = 0

        # 飞书每日数据追踪器
        self.feishu_tracker = FeishuDailyTracker()
        self._data_sync_tick = 0
        self._last_sync_at_22 = False  # 记录今天是否已经在22点同步过

        # 音频设备检测器
        self.audio_detector = AudioDeviceDetector()
        self.audio_detector.set_failure_callback(self._on_audio_device_failed)

        self.silent_start = silent_start
        self.drag_position = None

        self.init_ui()
        self.init_tray()
        self.set_autostart(True)
        self.setup_timer()
        # 创建小浮球
        self.floating_ball = FloatingBall(self)
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
        self.widget_height = 410  # 增加高度以容纳故障率显示
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

        # 故障率显示
        self.failure_rate_label = QLabel('🔊 设备故障：0 次')
        self.failure_rate_label.setFont(QFont('Poppins, Microsoft YaHei, Arial', 11))
        self.failure_rate_label.setAlignment(Qt.AlignCenter)
        self.failure_rate_label.setStyleSheet('color: #b0aea5; font-weight: 500; padding-top: 5px;')
        main_layout.addWidget(self.failure_rate_label)

        self.setLayout(main_layout)

    def position_to_right(self):
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        if '--center' in sys.argv:
            x = (screen_width - self.widget_width) // 2
            y = (screen_height - self.widget_height) // 2
            print(f"窗口居中显示：({x}, {y})")
        else:
            margin = 10
            x = screen_width - self.widget_width - margin
            y = (screen_height - self.widget_height) // 2
            print(f"窗口右侧显示：({x}, {y})")

        print(f"屏幕分辨率：{screen_width} x {screen_height}")
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
            print(f'设置自启动失败：{e}')
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
        try:
            if self.isVisible():
                self.hide()
                self.timer.stop()
            else:
                self.show()
                self.activateWindow()
                self.raise_()
                self.timer.start(1000)
        except Exception as e:
            print(f'[toggle_visibility 异常] {type(e).__name__}: {e}')

    def hide_to_edge(self):
        """隐藏窗口到桌面右侧边缘"""
        try:
            # 保存当前位置
            self._last_x = self.x()
            self._last_y = self.y()
            
            screen = QApplication.primaryScreen()
            if screen:
                screen_geometry = screen.geometry()
                # 隐藏到右侧边缘，只露出一个小边（约5像素）
                edge_width = 5
                x = screen_geometry.width() - edge_width
                y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
                self.timer.stop()
                self._is_hidden_to_edge = True
                print(f"已隐藏到右侧边缘，位置：({x}, {y})")
                # 确保窗口在最上层
                self.activateWindow()
                self.raise_()
        except Exception as e:
            print(f'[hide_to_edge 异常] {type(e).__name__}: {e}')

    def show_from_edge(self):
        """从右侧边缘显示窗口"""
        try:
            screen = QApplication.primaryScreen()
            if screen:
                # 恢复到之前的位置
                if hasattr(self, '_last_x') and hasattr(self, '_last_y'):
                    x = self._last_x
                    y = self._last_y
                else:
                    screen_geometry = screen.geometry()
                    x = screen_geometry.width() - self.width()
                    y = (screen_geometry.height() - self.height()) // 2
                self.move(x, y)
                self.show()
                self.activateWindow()
                self.raise_()
                self.timer.start(1000)
                self._is_hidden_to_edge = False
                print(f"已从边缘恢复，位置：({x}, {y})")
        except Exception as e:
            print(f'[show_from_edge 异常] {type(e).__name__}: {e}')

    def setup_edge_watcher(self):
        """设置边缘检测鼠标监视器"""
        self._is_hidden_to_edge = False
        self._edge_watch_timer = QTimer()
        self._edge_watch_timer.timeout.connect(self._check_mouse_at_edge)
        self._edge_watch_timer.start(100)  # 每100ms检测一次
        self._hide_delay_timer = QTimer()
        self._hide_delay_timer.setSingleShot(True)
        self._hide_delay_timer.timeout.connect(self.hide_to_edge)

    def _check_mouse_at_edge(self):
        """检测鼠标位置，自动显示/隐藏"""
        try:
            cursor_pos = QCursor.pos()
            screen = QApplication.primaryScreen()
            if not screen:
                return
            screen_geometry = screen.geometry()
            trigger_zone = 50  # 触发区域宽度（像素）

            if self._is_hidden_to_edge:
                # 窗口隐藏时：检测鼠标在右侧边缘就显示
                if cursor_pos.x() >= screen_geometry.width() - trigger_zone:
                    self.show_from_edge()
            else:
                # 窗口显示时：检测鼠标不在窗口区域就延迟隐藏
                # 获取窗口区域
                window_rect = self.geometry()
                # 添加一点额外空间，防止鼠标稍微离开就立即隐藏
                hover_zone = QRect(
                    window_rect.x() - 20,
                    window_rect.y() - 20,
                    window_rect.width() + 40,
                    window_rect.height() + 40
                )
                
                if not hover_zone.contains(cursor_pos):
                    # 鼠标不在窗口区域，延迟隐藏
                    if not self._hide_delay_timer.isActive():
                        self._hide_delay_timer.start(500)  # 500ms延迟
                else:
                    # 鼠标在窗口区域，取消隐藏
                    if self._hide_delay_timer.isActive():
                        self._hide_delay_timer.stop()
        except Exception as e:
            print(f'[_check_mouse_at_edge 异常] {type(e).__name__}: {e}')

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
            print(f'[_sync_buttons 异常] {type(e).__name__}: {e}')

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
            print(f'[on_start_clicked 异常] {type(e).__name__}: {e}')

    def on_pause_clicked(self):
        try:
            if self.timer_state != 'running':
                return
            remaining = self.interval_minutes * 60 - (datetime.now() - self.start_time).total_seconds()
            self.remaining_when_paused = max(remaining, 0)
            self.timer_state = 'paused'
            self._sync_buttons()
        except Exception as e:
            print(f'[on_pause_clicked 异常] {type(e).__name__}: {e}')

    def _reset_timer_to_idle(self):
        try:
            self.timer_state = 'idle'
            self.start_time = None
            self.remaining_when_paused = None
            self._sync_buttons()
        except Exception as e:
            print(f'[_reset_timer_to_idle 异常] {type(e).__name__}: {e}')

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

        # 倒计时结束
        if remaining <= 0:
            self.open_random_video()
            self.study_hours_today += 1
            self.update_study_display()
            self._reset_timer_to_idle()

    def _handle_paused(self, now):
        """处理暂停状态 - 显示暂停时间"""
        mins = int(self.remaining_when_paused // 60)
        secs = int(self.remaining_when_paused % 60)
        self.time_label.setText(f'⏸ 已暂停：{mins:02d}:{secs:02d}')

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

    def fetch_weather(self):
        """获取天气信息（占位方法）"""
        # 天气功能暂未实现，直接返回
        pass

    def update_display(self):
        try:
            now = datetime.now()

            # --- 日期变化重置 ---
            if now.date() != self.current_date:
                # 先同步昨天的数据到飞书
                if self.current_date:
                    self.feishu_tracker.sync_to_feishu(
                        self.study_hours_today,
                        self.computer_usage_hours_today
                    )
                # 重置数据
                self.played_today = set()
                self.study_hours_today = 0
                self.computer_usage_hours_today = 0
                self.computer_usage_reminder_given_at = None
                self.current_date = now.date()
                self._last_sync_at_22 = False  # 新的一天，重置同步标记
                self.update_study_display()
                self.update_computer_usage_display()
                # 通知追踪器日期变化
                self.feishu_tracker.check_date_change()
                print(f'新的一天，数据已重置: {self.current_date}')

            # --- 22 点自动同步数据到飞书 ---
            if now.hour == 22 and not self._last_sync_at_22:
                print(f'[22点自动同步] 正在同步数据到飞书...')
                self.feishu_tracker.sync_to_feishu(
                    self.study_hours_today,
                    self.computer_usage_hours_today
                )
                self._last_sync_at_22 = True
                self.tray_icon.showMessage(
                    '📊 数据已同步',
                    '今日数据已自动同步到飞书多维表格',
                    QSystemTrayIcon.Information,
                    3000
                )

            # --- 状态机路由 ---
            if self.timer_state == 'idle':
                self._handle_idle()
            elif self.timer_state == 'running':
                self._handle_running(now)
            elif self.timer_state == 'paused':
                self._handle_paused(now)

            # --- 22:00 倒计时（统一更新，避免重复请求） ---
            self._update_countdown(now)

            # --- 每 15 秒电池检测（合并窗口，避免 30/15 冲突） ---
            self._battery_tick += 1
            if self._battery_tick >= 15:
                self._battery_tick = 0
                self.update_battery_status()

            # --- 每 30 分钟天气刷新（与电池合并判断） ---
            self._weather_tick += 1
            if self._weather_tick >= 1800:
                self._weather_tick = 0
                self.fetch_weather()

            # --- 每 5 分钟同步数据到飞书 ---
            self._data_sync_tick += 1
            if self._data_sync_tick >= 300:
                self._data_sync_tick = 0
                self.feishu_tracker.sync_to_feishu(
                    self.study_hours_today,
                    self.computer_usage_hours_today
                )
                # 更新故障率显示
                self.update_failure_rate_display()

            # --- 电脑使用时长累加与提醒 ---
            self.update_computer_usage(now)

            # --- 音频设备检测（每5分钟检测一次） ---
            self.audio_detector.tick()

        except Exception as e:
            print(f'[update_display 异常] {type(e).__name__}: {e}')
            traceback.print_exc()


    def update_study_display(self):
        """更新学习时长显示"""
        h = self.study_hours_today
        self.study_progress_label.setText(f'📚 学习时长：{h}小时')
        self.study_progress_bar.setValue(h)

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

        # 每 3 小时提醒一次（取整除判断）
        current_cycle = int(self.computer_usage_hours_today / 3)
        last_cycle = int((self.computer_usage_hours_today - 1/3600) / 3) if self.computer_usage_hours_today >= 1/3600 else 0

        if current_cycle > last_cycle or (current_cycle > 0 and self.computer_usage_reminder_given_at != current_cycle):
            self.show_computer_usage_reminder()
            self.computer_usage_reminder_given_at = current_cycle

    def show_computer_usage_reminder(self):
        """电脑使用 3 小时后提醒，打开护眼视频"""
        video_url = 'https://www.bilibili.com/video/BV14Y4y1N7PW/?spm_id_from=333.1387.favlist.content.click'
        open_url(video_url)
        self.tray_icon.showMessage(
            '💻 电脑使用时间过长',
            '已经连续使用 3 小时了，看看护眼视频休息一下眼睛吧~',
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

    def _on_audio_device_failed(self, device_name):
        """音频设备故障回调"""
        print(f'[音频设备] 检测到设备故障: {device_name}')
        self.feishu_tracker.record_device_failure()
        self.update_failure_rate_display()
        self.tray_icon.showMessage(
            '🔊 音频设备故障',
            f'检测到设备异常：{device_name}\n请检查设备连接',
            QSystemTrayIcon.Warning,
            5000
        )

    def update_failure_rate_display(self):
        """更新设备故障显示"""
        try:
            failure_count = self.feishu_tracker.get_device_failure_count_today()
            self.failure_rate_label.setText(f'🔊 设备故障：{failure_count} 次')
        except Exception as e:
            print(f'[update_failure_rate_display 异常] {e}')

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
            print(f'获取电池状态失败：{e}')

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
                        print(f'B 站 API 返回错误 code={code}, msg={data.get("message")} (尝试 {attempt+1}/3)')
                        break

                    medias = data.get('data', {}).get('medias') or []
                    if not medias:
                        break

                    for media in medias:
                        bvid = media.get('bvid')
                        if bvid:
                            videos.append(f'https://www.bilibili.com/video/{bvid}')

                    if len(medias) < page_size:
                        break
                    page += 1

                if videos:
                    print(f'获取到 {len(videos)} 个收藏视频（{page} 页，第{attempt+1}次尝试）')
                    return videos

            except Exception as e:
                print(f'获取视频列表异常 (尝试 {attempt+1}/3): {e}')

            if attempt < 2:
                time.sleep(2)

        # 兜底方案
        print('API 3 次全部失败，尝试从收藏夹页面提取视频链接...')
        try:
            page_url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create'
            resp = requests.get(page_url, headers={'User-Agent': user_agents[0], 'Referer': 'https://www.bilibili.com'}, timeout=10)
            import re
            bvids = re.findall(r'BV[a-zA-Z0-9]{10}', resp.text)
            seen = set()
            unique = []
            for bv in bvids:
                if bv not in seen:
                    seen.add(bv)
                    unique.append(bv)
            if unique:
                print(f'从页面兜底提取到 {len(unique)} 个视频')
                return [f'https://www.bilibili.com/video/{bv}' for bv in unique]
        except Exception as e:
            print(f'页面兜底也失败了：{e}')

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
                        print('当天视频已全部播放过，重置记录')
                        self.played_today = set()
                        remaining = videos

                    video_url = random.choice(remaining)
                    self.played_today.add(video_url)
                    print(f'打开视频：{video_url} (今日已播 {len(self.played_today)}/{len(self.video_list)})')
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
                print(f'[open_random_video 回调异常] {type(e).__name__}: {e}')
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
            print(f'[mousePressEvent 异常] {type(e).__name__}: {e}')

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() == Qt.LeftButton:
                self.move(event.globalPos() - self.drag_position)
                event.accept()
        except Exception as e:
            print(f'[mouseMoveEvent 异常] {type(e).__name__}: {e}')

    def closeEvent(self, event):
        try:
            event.ignore()
            self.hide_to_edge()
        except Exception as e:
            print(f'[closeEvent 异常] {type(e).__name__}: {e}')

    def quit_app(self):
        try:
            self.timer.stop()
            self.tray_icon.hide()
            QApplication.quit()
        except Exception as e:
            print(f'[quit_app 异常] {type(e).__name__}: {e}')


def main():
    single = SingleInstanceChecker()

    if single.is_already_running():
        print('休息提醒程序已经在运行中！')
        if '--silent' not in sys.argv:
            a = QApplication(sys.argv)
            QMessageBox.warning(None, '已在运行', '程序已在运行中！\n请检查系统托盘图标。')
        sys.exit(0)

    # 先创建一个临时的追踪器实例，用于记录早期崩溃
    early_tracker = FeishuDailyTracker()

    def excepthook(exc_type, exc_value, exc_tb):
        import traceback
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        # 记录崩溃到飞书追踪器
        try:
            early_tracker.record_crash()
        except:
            pass
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

    # 更新异常处理器，使用 widget 的追踪器
    def widget_excepthook(exc_type, exc_value, exc_tb):
        import traceback
        log_dir = os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, 'crash.log'), 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'[{datetime.now().isoformat()}] 未捕获异常：{exc_type.__name__}: {exc_value}\n')
            traceback.print_exception(exc_type, exc_value, exc_tb, file=f)
        # 记录崩溃到飞书追踪器
        try:
            widget.feishu_tracker.record_crash()
        except:
            pass
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
        print(f'WM_SETICON error: {e}')

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
