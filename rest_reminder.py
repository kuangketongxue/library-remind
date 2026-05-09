"""
桌面休息提醒挂件
每小时提醒休息，并随机打开B站收藏夹中的视频
监控电池充电状态
"""
import sys
import time
import webbrowser
import random
import requests
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout, QPushButton, QMessageBox)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon, QFont
import json
import subprocess
import re
import psutil
import os
import tempfile
import atexit
import winreg


class SingleInstanceChecker:
    """单实例检查器 - 确保程序只运行一个实例"""
    def __init__(self):
        self.lock_file = None
        self.lock_path = os.path.join(tempfile.gettempdir(), 'rest_reminder.lock')
        self.lock_handle = None
        
    def is_already_running(self):
        """检查程序是否已经在运行"""
        try:
            # 在Windows上使用文件独占锁
            import msvcrt
            
            # 尝试打开或创建锁文件
            try:
                # 以读写模式打开，如果不存在则创建
                self.lock_handle = open(self.lock_path, 'w')
                # 尝试获取独占锁（非阻塞）
                msvcrt.locking(self.lock_handle.fileno(), msvcrt.LK_NBLCK, 1)
                
                # 成功获取锁，写入当前PID
                self.lock_handle.write(str(os.getpid()))
                self.lock_handle.flush()
                
                self.lock_file = self.lock_path
                # 注册退出时删除锁文件
                atexit.register(self.cleanup)
                return False
                
            except IOError:
                # 无法获取锁，说明已有实例在运行
                if self.lock_handle:
                    self.lock_handle.close()
                    self.lock_handle = None
                return True
                
        except ImportError:
            # 如果msvcrt不可用（非Windows），使用原来的方法
            return self._fallback_check()
        except Exception as e:
            print(f'单实例检查失败: {e}')
            return False
    
    def _fallback_check(self):
        """备用检查方法（用于非Windows系统）"""
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
            print(f'备用单实例检查失败: {e}')
            return False
    
    def cleanup(self):
        """清理锁文件"""
        try:
            # 释放文件锁
            if self.lock_handle:
                try:
                    import msvcrt
                    msvcrt.locking(self.lock_handle.fileno(), msvcrt.LK_UNLCK, 1)
                except:
                    pass
                self.lock_handle.close()
                self.lock_handle = None
            
            # 删除锁文件
            if self.lock_file and os.path.exists(self.lock_file):
                os.remove(self.lock_file)
        except:
            pass


STRETCH_EXERCISES = [
    "拉腿*2",
    "鲤鱼打挺",
    "利于后入",
    "跪着向后",
    "蹲着手拉手",
    "坐地上打开双腿向前",
    "靠墙拉双手后肱肌",
    "跪着拉双手后肱肌",
    "躺床上拉双手前肱肌",
    "躺地上四肢朝天",
]

# 飞书多维表格配置
FEISHU_BASE_TOKEN = "DcJzbLadCaGbGws2ZekchGHhnVe"
FEISHU_TABLE_ID = "tbl9DT9qniE63BH7"
FEISHU_VIEW_NAME = "时长"
# lark-cli 完整路径（npm 全局安装，Python subprocess PATH 中找不到）
LARK_CLI = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'lark-cli.cmd')


class RestReminderWidget(QWidget):
    def __init__(self, silent_start=False):
        super().__init__()
        self.interval_minutes = 60  # 每60分钟提醒一次
        self.start_time = None
        self.remaining_when_paused = None
        self.timer_state = 'idle'  # idle / running / paused
        self._battery_tick = 0  # 每 15 次 tick 刷新一次电池
        self.video_list = []
        self.played_today = set()  # 当天已播放的视频URL，避免重复
        self.last_charging_state = None  # 记录上次充电状态
        self.battery_warning_shown = False  # 是否已显示电池警告
        self.silent_start = silent_start  # 静默启动模式
        self.battery_notification_active = False  # 电池通知是否正在显示
        self.current_date = datetime.now().date()  # 记录当前日期，用于检测日期变化
        self.feishu_hours = None  # 飞书记录的工作时长（小时数）
        self.feishu_stretch_items = []  # 飞书记录的拉伸动作列表
        
        self.init_ui()
        self.position_to_right()  # 定位到屏幕右侧
        self.init_tray()
        self.set_autostart(True)  # 启动时自动注册开机自启动
        self.setup_timer()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('休息提醒')
        self.widget_width = 340
        self.widget_height = 370
        self.setGeometry(100, 100, self.widget_width, self.widget_height)
        
        # 设置窗口置顶和无边框（移除Tool标志，让窗口可以在任务栏显示）
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        # 设置可爱图标（任务栏+托盘通用）
        ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
        self.app_icon = QIcon(ico_path)
        self.setWindowIcon(self.app_icon)
        
        # 设置半透明背景
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 230);
                border-radius: 10px;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 15px;
            }
            QPushButton#closeBtn {
                background-color: transparent;
                color: #CCCCCC;
                border: none;
                font-size: 20px;
                font-weight: bold;
                padding: 0px;
                margin: 0px;
            }
            QPushButton#closeBtn:hover {
                color: #FFFFFF;
                background-color: rgba(255, 255, 255, 30);
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #333;
                font-size: 14px;
            }
            QProgressBar::chunk {
                background-color: #00AFF0;
                border-radius: 3px;
            }
            #battery_bar::chunk {
                background-color: #4CAF50;
            }
            #battery_bar_low::chunk {
                background-color: #FF5252;
            }
            #countdown_bar::chunk {
                background-color: #FF9800;
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 10)
        main_layout.setSpacing(5)
        
        # 顶部布局：标题 + 最小化按钮
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0)
        
        # 标题
        self.title_label = QLabel('⏰ 休息提醒')
        self.title_label.setFont(QFont('Microsoft YaHei', 13, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_layout.addWidget(self.title_label)
        
        # 弹簧，把按钮推到右边
        top_layout.addStretch()
        
        # 最小化按钮
        self.close_btn = QPushButton('−')  # 使用减号符号
        self.close_btn.setObjectName('closeBtn')
        self.close_btn.setFixedSize(30, 30)
        self.close_btn.setCursor(Qt.PointingHandCursor)
        self.close_btn.setToolTip('最小化到任务栏')
        self.close_btn.clicked.connect(self.showMinimized)  # 最小化到任务栏
        top_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(top_layout)
        
        # 时间显示
        self.time_label = QLabel('距离下次休息: 60:00')
        self.time_label.setFont(QFont('Microsoft YaHei', 15))
        self.time_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.time_label)

        # 按钮布局：开始 / 暂停
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.start_btn = QPushButton('▶ 开始')
        self.start_btn.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        self.start_btn.setFixedHeight(32)
        self.start_btn.setCursor(Qt.PointingHandCursor)
        self.start_btn.setStyleSheet("""
            QPushButton { background-color: #4CAF50; color: white; border: none; border-radius: 6px; padding: 0 18px; }
            QPushButton:hover { background-color: #45A049; }
        """)
        self.start_btn.clicked.connect(self.on_start_clicked)
        btn_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton('⏸ 暂停')
        self.pause_btn.setFont(QFont('Microsoft YaHei', 11, QFont.Bold))
        self.pause_btn.setFixedHeight(32)
        self.pause_btn.setCursor(Qt.PointingHandCursor)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setStyleSheet("""
            QPushButton { background-color: #FF9800; color: white; border: none; border-radius: 6px; padding: 0 18px; }
            QPushButton:hover { background-color: #E68A00; }
            QPushButton:disabled { background-color: #666; color: #999; }
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

        # 22:00 倒计时进度条
        self.countdown_label = QLabel('⏳ 距离22:00:')
        self.countdown_label.setFont(QFont('Microsoft YaHei', 12))
        self.countdown_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.countdown_label)

        self.countdown_bar = QProgressBar()
        self.countdown_bar.setObjectName('countdown_bar')
        self.countdown_bar.setMaximum(100)
        self.countdown_bar.setValue(0)
        self.countdown_bar.setTextVisible(True)
        self.countdown_bar.setFormat('%p%')
        self.countdown_bar.setMaximumHeight(20)
        main_layout.addWidget(self.countdown_bar)

        # 学习时长进度条（14小时 = 100%）
        self.study_progress_label = QLabel('📊 学习时长: 加载中...')
        self.study_progress_label.setFont(QFont('Microsoft YaHei', 12))
        self.study_progress_label.setAlignment(Qt.AlignCenter)
        self.study_progress_label.setStyleSheet('color: #FFD700; font-weight: bold;')
        main_layout.addWidget(self.study_progress_label)

        self.study_progress_bar = QProgressBar()
        self.study_progress_bar.setObjectName('study_bar')
        self.study_progress_bar.setMaximum(14)  # 14小时目标
        self.study_progress_bar.setValue(0)
        self.study_progress_bar.setTextVisible(True)
        self.study_progress_bar.setFormat('%v / 14 小时')
        self.study_progress_bar.setMaximumHeight(22)
        self.study_progress_bar.setStyleSheet("""
            QProgressBar { border: 2px solid #555; border-radius: 5px; text-align: center; background-color: #333; font-size: 12px; }
            QProgressBar::chunk { background-color: #FFD700; border-radius: 3px; }
        """)
        main_layout.addWidget(self.study_progress_bar)

        # 拉伸统计
        self.stretch_label = QLabel('🧘 拉伸: 0 个')
        self.stretch_label.setFont(QFont('Microsoft YaHei', 12))
        self.stretch_label.setAlignment(Qt.AlignCenter)
        self.stretch_label.setStyleSheet('color: #4CAF50; font-weight: bold;')
        main_layout.addWidget(self.stretch_label)
        
        # 电池状态区域
        battery_layout = QHBoxLayout()
        
        # 电池图标和状态文字
        self.battery_label = QLabel('🔋 检测中...')
        self.battery_label.setFont(QFont('Microsoft YaHei', 12))
        battery_layout.addWidget(self.battery_label)
        
        main_layout.addLayout(battery_layout)
        
        # 电池电量进度条
        self.battery_bar = QProgressBar()
        self.battery_bar.setObjectName('battery_bar')
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat('%p%')
        self.battery_bar.setMaximumHeight(20)
        main_layout.addWidget(self.battery_bar)
        
        self.setLayout(main_layout)
    
    def position_to_right(self):
        """将窗口定位到屏幕右侧中间"""
        screen = QApplication.desktop().screenGeometry()
        screen_width = screen.width()
        screen_height = screen.height()
        
        # 检查是否有--center参数，如果有则居中显示
        if '--center' in sys.argv:
            # 居中显示
            x = (screen_width - self.widget_width) // 2
            y = (screen_height - self.widget_height) // 2
            print(f"窗口居中显示: ({x}, {y})")
        else:
            # 计算位置：屏幕右侧，垂直居中，留出一些边距
            margin = 10  # 距离屏幕边缘的距离
            x = screen_width - self.widget_width - margin
            y = (screen_height - self.widget_height) // 2
            print(f"窗口右侧显示: ({x}, {y})")
        
        print(f"屏幕分辨率: {screen_width} x {screen_height}")
        self.move(x, y)
        
    def _get_autostart_cmd(self):
        """获取自动启动的命令行"""
        script = os.path.abspath(sys.argv[0] if sys.argv[0].endswith('.py') else __file__)
        pythonw = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
        if not os.path.exists(pythonw):
            pythonw = sys.executable
        return f'"{pythonw}" "{script}" --startup'

    def is_autostart_enabled(self):
        """检查是否已设置开机自启动（注册表）"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, winreg.KEY_READ
            )
            val, _ = winreg.QueryValueEx(key, 'RestReminder')
            winreg.CloseKey(key)
            return bool(val)
        except (FileNotFoundError, OSError):
            return False

    def set_autostart(self, enabled):
        """设置或取消开机自启动（注册表）"""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Run',
                0, winreg.KEY_SET_VALUE
            )
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
            print(f'设置自启动失败: {e}')
            return False

    def toggle_autostart(self):
        """切换开机自启动状态"""
        new_state = not self.is_autostart_enabled()
        if self.set_autostart(new_state):
            self.autostart_action.setChecked(new_state)
            tip = '已开启' if new_state else '已关闭'
            self.tray_icon.showMessage('休息提醒', f'开机自启动{tip}', QSystemTrayIcon.Information, 2000)

    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('休息提醒 - 双击显示/隐藏')

        # 双击托盘图标切换显示/隐藏
        self.tray_icon.activated.connect(self.on_tray_icon_activated)

        # 创建托盘菜单
        tray_menu = QMenu()

        toggle_action = QAction('显示/隐藏', self)
        toggle_action.triggered.connect(self.toggle_visibility)
        tray_menu.addAction(toggle_action)

        tray_menu.addSeparator()

        # 开机自启动开关（注册表方式，零外部依赖）
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
        
        # 使用可爱图标
        self.tray_icon.setIcon(self.app_icon)
        self.tray_icon.show()
    
    def on_tray_icon_activated(self, reason):
        """托盘图标激活事件"""
        if reason == QSystemTrayIcon.DoubleClick:
            self.toggle_visibility()
    
    def toggle_visibility(self):
        """切换窗口显示/隐藏"""
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.activateWindow()  # 激活窗口
            self.raise_()  # 置顶显示
        
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)  # 每秒更新一次

        # 飞书数据定时拉取（每30秒，近实时同步）
        self.feishu_timer = QTimer()
        self.feishu_timer.timeout.connect(self.fetch_feishu_data)
        QTimer.singleShot(5000, self.fetch_feishu_data)  # 启动5秒后首次拉取
        self.feishu_timer.start(30000)  # 30秒
        
    _BTN_CONFIG = {
        'idle':    {'start_en': True,  'start_txt': '▶ 开始', 'pause_en': False, 'pause_txt': '⏸ 暂停'},
        'running': {'start_en': False, 'start_txt': '▶ 开始', 'pause_en': True,  'pause_txt': '⏸ 暂停'},
        'paused':  {'start_en': True,  'start_txt': '▶ 继续', 'pause_en': False, 'pause_txt': '⏸ 已暂停'},
    }

    def _sync_buttons(self):
        c = self._BTN_CONFIG[self.timer_state]
        self.start_btn.setEnabled(c['start_en'])
        self.start_btn.setText(c['start_txt'])
        self.pause_btn.setEnabled(c['pause_en'])
        self.pause_btn.setText(c['pause_txt'])

    def on_start_clicked(self):
        if self.timer_state not in ('idle', 'paused'):
            return
        if self.timer_state == 'idle':
            self.start_time = datetime.now()
        else:
            self.start_time = datetime.now() - timedelta(seconds=(self.interval_minutes * 60 - self.remaining_when_paused))
        self.remaining_when_paused = None
        self.timer_state = 'running'
        self._sync_buttons()

    def on_pause_clicked(self):
        if self.timer_state != 'running':
            return
        remaining = self.interval_minutes * 60 - (datetime.now() - self.start_time).total_seconds()
        self.remaining_when_paused = max(remaining, 0)
        self.timer_state = 'paused'
        self._sync_buttons()

    def _reset_timer_to_idle(self):
        self.timer_state = 'idle'
        self.start_time = None
        self.remaining_when_paused = None
        self._sync_buttons()

    def update_display(self):
        """更新显示内容"""
        now = datetime.now()

        # 检查日期是否变化（过了零点）
        if now.date() != self.current_date:
            self.played_today = set()
            self.feishu_hours = None
            self.feishu_stretch_items = []
            self.current_date = now.date()
            self.update_feishu_display()
            self.fetch_feishu_data()
            print(f'新的一天，飞书数据已重置: {self.current_date}')

        total_seconds = self.interval_minutes * 60

        if self.timer_state == 'idle':
            self.time_label.setText(f'距离下次休息: {self.interval_minutes:02d}:00')
            self.progress_bar.setValue(0)
        elif self.timer_state == 'running':
            elapsed = (now - self.start_time).total_seconds()
            remaining_seconds = total_seconds - elapsed

            if remaining_seconds <= 0:
                self.open_random_video()
                self.show_feishu_reminder()
                self.show_stretch_reminder()
                self._reset_timer_to_idle()
                self.time_label.setText(f'距离下次休息: {self.interval_minutes:02d}:00')
                self.progress_bar.setValue(100)
                return

            minutes = int(remaining_seconds // 60)
            seconds = int(remaining_seconds % 60)
            self.time_label.setText(f'距离下次休息: {minutes:02d}:{seconds:02d}')
            progress = int((elapsed / total_seconds) * 100)
            self.progress_bar.setValue(progress)
        elif self.timer_state == 'paused':
            remaining = self.remaining_when_paused or 0
            minutes = int(remaining // 60)
            seconds = int(remaining % 60)
            self.time_label.setText(f'⏸ 已暂停: {minutes:02d}:{seconds:02d}')
            elapsed = total_seconds - remaining
            progress = int((elapsed / total_seconds) * 100)
            self.progress_bar.setValue(progress)

        # 22:00倒计时进度条（4:30=0%，22:00=100%）
        start_minutes = 4 * 60 + 30
        end_minutes = 22 * 60
        total_span = end_minutes - start_minutes
        current_minutes = now.hour * 60 + now.minute + now.second / 60
        if current_minutes >= end_minutes:
            countdown_pct = 100
        elif current_minutes <= start_minutes:
            countdown_pct = 0
        else:
            countdown_pct = int(((current_minutes - start_minutes) / total_span) * 100)
        self.countdown_bar.setValue(countdown_pct)

        # 电池状态每 15 秒刷新一次（ACPI 调用不必每秒跑）
        self._battery_tick += 1
        if self._battery_tick >= 15:
            self._battery_tick = 0
            self.update_battery_status()
    
    def update_battery_status(self):
        """更新电池状态显示"""
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                # 没有电池（台式机）
                self.battery_label.setText('🖥️ 台式机（无电池）')
                self.battery_bar.setValue(100)
                self.battery_bar.setObjectName('battery_bar')
                self.battery_bar.setStyleSheet('')
                return
            
            # 获取电池信息
            percent = battery.percent
            plugged = battery.power_plugged
            
            # 更新电池电量进度条
            self.battery_bar.setValue(int(percent))
            
            # 根据电量设置进度条颜色
            if percent <= 20:
                self.battery_bar.setObjectName('battery_bar_low')
                self.battery_bar.setStyleSheet("""
                    QProgressBar::chunk {
                        background-color: #FF5252;
                    }
                """)
            else:
                self.battery_bar.setObjectName('battery_bar')
                self.battery_bar.setStyleSheet("""
                    QProgressBar::chunk {
                        background-color: #4CAF50;
                    }
                """)
            
            # 更新状态文字
            if plugged:
                if percent >= 100:
                    icon = '🔌'
                    status = '已充满'
                else:
                    icon = '⚡'
                    status = '充电中'
                self.battery_label.setText(f'{icon} {status}')
                
                # 重新充电后，关闭之前的断电警告，并重置警告状态
                if self.battery_notification_active:
                    # 隐藏通知（通过显示一个空通知来"关闭"之前的通知）
                    self.tray_icon.showMessage('', '', QSystemTrayIcon.NoIcon, 1)
                    self.battery_notification_active = False
                
                # 重置警告状态，允许下次断电时再次提醒
                self.battery_warning_shown = False
            else:
                icon = '🔋'
                if percent <= 20:
                    status = '电量低'
                    icon = '🪫'
                elif percent <= 50:
                    status = '电量中'
                else:
                    status = '使用电池'
                self.battery_label.setText(f'{icon} {status}')
                
                # 检测充电状态变化：从充电变为未充电
                if self.last_charging_state is True and not plugged:
                    # 只在第一次断电时显示警告
                    if not self.battery_warning_shown:
                        self.show_battery_warning(percent)
                        self.battery_warning_shown = True
                        self.battery_notification_active = True
            
            # 记录当前充电状态
            self.last_charging_state = plugged
            
        except Exception as e:
            self.battery_label.setText('❌ 电池状态获取失败')
            print(f'获取电池状态失败: {e}')
    
    def show_battery_warning(self, percent):
        """显示电池警告（只显示一次）"""
        self.tray_icon.showMessage(
            '⚠️ 电源已断开',
            f'检测到电脑未在充电！\n当前电量: {percent}%\n建议连接电源以保持最佳性能。',
            QSystemTrayIcon.Warning,
            5000
        )
        
        # 窗口闪烁提醒（如果窗口可见）
        if self.isVisible():
            self.setWindowOpacity(0.5)
            QTimer.singleShot(200, lambda: self.setWindowOpacity(1.0))
            QTimer.singleShot(400, lambda: self.setWindowOpacity(0.5))
            QTimer.singleShot(600, lambda: self.setWindowOpacity(1.0))
    
    def fetch_feishu_data(self):
        """从飞书多维表格拉取今日工作时长和拉伸数据（异步，不阻塞主线程）"""
        from PyQt5.QtCore import QThread, pyqtSignal

        class FeishuFetchThread(QThread):
            finished = pyqtSignal(object)  # 传回 (hours, stretch_items) 或 None

            def run(self):
                try:
                    cmd = [
                        LARK_CLI, 'base', '+record-list',
                        '--base-token', FEISHU_BASE_TOKEN,
                        '--table-id', FEISHU_TABLE_ID,
                        '--view-id', FEISHU_VIEW_NAME,
                        '--limit', '30',
                        '--format', 'json'
                    ]
                    si = subprocess.STARTUPINFO()
                    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    si.wShowWindow = subprocess.SW_HIDE
                    result = subprocess.run(
                        cmd, capture_output=True,
                        timeout=10,
                        startupinfo=si,
                        creationflags=0x08000000
                    )
                    if result.returncode != 0:
                        self.finished.emit(None)
                        return

                    resp = json.loads(result.stdout.decode('utf-8'))
                    if not resp.get('ok'):
                        self.finished.emit(None)
                        return

                    records = resp['data']['data']
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    today_data = None
                    for rec in reversed(records):
                        if rec and rec[0] and str(rec[0]).startswith(today_str):
                            today_data = rec
                            break

                    if not today_data:
                        self.finished.emit(None)
                        return

                    hours_val = today_data[1] if len(today_data) > 1 else None
                    hours = None
                    if hours_val and isinstance(hours_val, list) and hours_val:
                        match = re.search(r'(\d+)', str(hours_val[0]))
                        hours = int(match.group(1)) if match else None

                    stretch_val = today_data[2] if len(today_data) > 2 else None
                    stretch_items = stretch_val if stretch_val and isinstance(stretch_val, list) else []

                    self.finished.emit((hours, stretch_items))
                except Exception as e:
                    print(f'[FeishuFetchThread] 飞书数据拉取失败: {e}')
                    self.finished.emit(None)

        def on_feishu_fetched(data):
            if data is None:
                return
            hours, stretch_items = data
            self.feishu_hours = hours
            self.feishu_stretch_items = stretch_items
            self.update_feishu_display()
            print(f'飞书数据已更新: 时长={self.feishu_hours}h, 拉伸={len(self.feishu_stretch_items)}个')

        self._feishu_thread = FeishuFetchThread()
        self._feishu_thread.finished.connect(on_feishu_fetched)
        self._feishu_thread.start()

    def update_feishu_display(self):
        """仅展示飞书数据，不叠加本地计数"""
        h = self.feishu_hours if self.feishu_hours is not None else 0

        if self.feishu_hours is not None:
            self.study_progress_label.setText(f'📊 学习时长: {h}h（飞书）')
        else:
            self.study_progress_label.setText('📊 学习时长: 飞书未记录')

        self.study_progress_bar.setValue(h)

        n = len(self.feishu_stretch_items)
        self.stretch_label.setText(f'🧘 拉伸: {n} 个（飞书）')

    def show_feishu_reminder(self):
        """提醒去飞书更新数据（不显示本地累加数）"""
        h = self.feishu_hours if self.feishu_hours is not None else 0
        self.tray_icon.showMessage(
            '📊 该更新飞书了',
            f'当前飞书记录：{h} 小时\n\n'
            '去飞书多维表格【每日追踪→时长】更新吧~',
            QSystemTrayIcon.Information,
            8000
        )

        # 窗口闪烁提醒
        if self.isVisible():
            original_style = self.study_progress_label.styleSheet()
            flash_style = 'color: #FF6B6B; font-weight: bold; background-color: rgba(255, 215, 0, 50);'
            self.study_progress_label.setStyleSheet(flash_style)
            QTimer.singleShot(500, lambda: self.study_progress_label.setStyleSheet(original_style))
            QTimer.singleShot(1000, lambda: self.study_progress_label.setStyleSheet(flash_style))
            QTimer.singleShot(1500, lambda: self.study_progress_label.setStyleSheet(original_style))
            QTimer.singleShot(2000, lambda: self.study_progress_label.setStyleSheet(flash_style))
            QTimer.singleShot(2500, lambda: self.study_progress_label.setStyleSheet(original_style))

    def show_stretch_reminder(self):
        """随机推荐一个拉伸动作（计数只看飞书）"""
        name = random.choice(STRETCH_EXERCISES)
        n = len(self.feishu_stretch_items)

        self.tray_icon.showMessage(
            f'🧘 拉伸时间！（飞书已记录 {n} 个）',
            f'{name}\n\n做完在飞书【拉伸】栏记一笔~',
            QSystemTrayIcon.Information,
            10000
        )

    def get_bilibili_videos(self):
        """
        获取B站收藏夹视频列表（分页拉取全部）
        带 3 次重试：网络抖动 / API 限流都能兜住
        """
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
                        print(f'B站API返回错误 code={code}, msg={data.get("message")} (尝试 {attempt+1}/3)')
                        break

                    medias = data.get('data', {}).get('medias') or []
                    if not medias:
                        break

                    for media in medias:
                        bvid = media.get('bvid')
                        if bvid:
                            videos.append(f'https://www.bilibili.com/video/{bvid}')

                    # 如果返回数量不足 page_size，说明是最后一页
                    if len(medias) < page_size:
                        break
                    page += 1

                if videos:
                    print(f'获取到 {len(videos)} 个收藏视频（{page} 页, 第{attempt+1}次尝试）')
                    return videos

            except Exception as e:
                print(f'获取视频列表异常 (尝试 {attempt+1}/3): {e}')

            # 重试前等 2 秒
            if attempt < 2:
                time.sleep(2)

        # 3 次都失败 → 用收藏夹页面的 bvid 正则兜底
        print('API 3 次全部失败，尝试从收藏夹页面提取视频链接...')
        try:
            page_url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create'
            resp = requests.get(page_url, headers={
                'User-Agent': user_agents[0],
                'Referer': 'https://www.bilibili.com',
            }, timeout=10)
            bvids = re.findall(r'BV[a-zA-Z0-9]{10}', resp.text)
            # 去重，保持顺序
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
            print(f'页面兜底也失败了: {e}')

        return []
    
    def open_random_video(self):
        """打开随机视频（异步获取，不阻塞主线程）"""
        from PyQt5.QtCore import QThread, pyqtSignal

        class VideoFetchThread(QThread):
            finished = pyqtSignal(list)

            def __init__(self, get_videos_fn):
                super().__init__()
                self._get_videos = get_videos_fn

            def run(self):
                try:
                    videos = self._get_videos()
                except Exception as e:
                    print(f'[VideoFetchThread] 获取视频异常: {e}')
                    videos = []
                self.finished.emit(videos)

        def on_videos_fetched(videos):
            self.video_list = videos
            if videos:
                remaining = [v for v in videos if v not in self.played_today]
                if not remaining:
                    print('当天视频已全部播放过，重置记录')
                    self.played_today = set()
                    remaining = videos

                video_url = random.choice(remaining)
                self.played_today.add(video_url)
                print(f'打开视频: {video_url} (今日已播 {len(self.played_today)}/{len(self.video_list)})')
                webbrowser.open(video_url)
                self.tray_icon.showMessage(
                    '休息时间到！',
                    f'已为您打开休息视频（今日第{len(self.played_today)}个），记得放松一下哦~',
                    QSystemTrayIcon.Information,
                    3000
                )
            else:
                fallback_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create'
                webbrowser.open(fallback_url)
                self.tray_icon.showMessage(
                    '休息时间到！',
                    '已为您打开收藏夹页面~',
                    QSystemTrayIcon.Information,
                    3000
                )

        # 等旧线程结束再启动新线程，避免信号冲突
        if hasattr(self, '_video_thread') and self._video_thread.isRunning():
            self._video_thread.wait(3000)

        self._video_thread = VideoFetchThread(self.get_bilibili_videos)
        self._video_thread.finished.connect(on_videos_fetched)
        self._video_thread.start()
    
    def mousePressEvent(self, event):
        """鼠标按下事件 - 用于拖动窗口"""
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 拖动窗口"""
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def closeEvent(self, event):
        """关闭事件 - 最小化到托盘而不是退出"""
        event.ignore()
        self.hide()
        # 静默模式下不显示任何提示
        if not self.silent_start and not hasattr(self, '_hide_tip_shown'):
            self.tray_icon.showMessage(
                '休息提醒',
                '程序已隐藏到系统托盘\n双击托盘图标可重新显示',
                QSystemTrayIcon.Information,
                3000
            )
            self._hide_tip_shown = True
    
    def quit_app(self):
        """退出应用"""
        self.feishu_timer.stop()
        self.tray_icon.hide()
        QApplication.quit()


def main():
    # 全局异常钩子：防止未捕获异常杀死进程
    def excepthook(exc_type, exc_value, exc_tb):
        import traceback
        print(f'[全局异常捕获] {exc_type.__name__}: {exc_value}')
        traceback.print_exception(exc_type, exc_value, exc_tb)
        # 不调用 sys.exit，让程序继续运行
    sys.excepthook = excepthook

    # 告诉 Windows 这是独立应用（否则任务栏用 pythonw.exe 的图标）
    import ctypes
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('RestReminder.RestReminder.1.0')

    # 单实例检查
    instance_checker = SingleInstanceChecker()
    if instance_checker.is_already_running():
        print('休息提醒程序已经在运行中！')
        print('如果您看到此消息但找不到程序窗口，请：')
        print('1. 检查系统托盘（任务栏右下角）是否有程序图标')
        print('2. 双击托盘图标可显示窗口')
        print('3. 或者先结束已运行的进程再重新启动')
        
        # 检查是否是静默启动，如果不是则显示对话框
        if '--silent' not in sys.argv and '--startup' not in sys.argv:
            # 创建临时应用以显示消息框
            temp_app = QApplication(sys.argv)
            QMessageBox.warning(
                None,
                '程序已在运行',
                '休息提醒程序已经在运行中！\n\n'
                '请检查系统托盘（任务栏右下角）是否有程序图标。\n'
                '双击托盘图标可显示窗口。\n\n'
                '如需重新启动，请先右键托盘图标选择"退出"。',
                QMessageBox.Ok
            )
        
        sys.exit(1)
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出程序

    # 设置应用程序图标（任务栏显示，用 .ico 获得多尺寸支持）
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cute_icon.ico')
    app.setWindowIcon(QIcon(ico_path))
    
    # 检查命令行参数，判断是否静默启动
    silent_start = '--silent' in sys.argv or '--startup' in sys.argv
    
    widget = RestReminderWidget(silent_start=silent_start)

    # 静默启动模式：直接隐藏窗口，只显示托盘图标
    if silent_start:
        widget.hide()
    else:
        widget.show()

    # 强制任务栏图标覆盖（setWindowIcon 对任务栏不可靠，用 WM_SETICON 直接设置）
    import ctypes
    hwnd = int(widget.winId())
    hicon = ctypes.windll.user32.LoadImageW(
        0, ico_path, 1, 0, 0, 0x00000010  # IMAGE_ICON, LR_LOADFROMFILE
    )
    if hicon:
        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon)  # WM_SETICON, ICON_BIG
        ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon)  # WM_SETICON, ICON_SMALL

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
