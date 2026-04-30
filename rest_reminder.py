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
import psutil
import os
import tempfile
import atexit


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


class RestReminderWidget(QWidget):
    def __init__(self, silent_start=False):
        super().__init__()
        self.interval_minutes = 60  # 每60分钟提醒一次
        self.start_time = datetime.now()
        self.video_list = []
        self.last_charging_state = None  # 记录上次充电状态
        self.battery_warning_shown = False  # 是否已显示电池警告
        self.silent_start = silent_start  # 静默启动模式
        self.battery_notification_active = False  # 电池通知是否正在显示
        self.study_hours_count = 0  # 学习小时计数
        self.current_date = datetime.now().date()  # 记录当前日期，用于检测日期变化
        
        self.init_ui()
        self.position_to_right()  # 定位到屏幕右侧
        self.init_tray()
        self.setup_timer()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('休息提醒')
        self.widget_width = 340
        self.widget_height = 220
        self.setGeometry(100, 100, self.widget_width, self.widget_height)
        
        # 设置窗口置顶和无边框（移除Tool标志，让窗口可以在任务栏显示）
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
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
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('%p%')
        main_layout.addWidget(self.progress_bar)
        
        # 学习时长统计提醒
        self.study_hours_label = QLabel('📊 已学习: 0 小时')
        self.study_hours_label.setFont(QFont('Microsoft YaHei', 12))
        self.study_hours_label.setAlignment(Qt.AlignCenter)
        self.study_hours_label.setStyleSheet('color: #FFD700; font-weight: bold;')
        main_layout.addWidget(self.study_hours_label)
        
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
        
        reset_position_action = QAction('重置位置到右侧', self)
        reset_position_action.triggered.connect(self.position_to_right)
        tray_menu.addAction(reset_position_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        
        # 使用默认图标（实际使用时应该提供图标文件）
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_MessageBoxInformation))
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
        
    def update_display(self):
        """更新显示内容"""
        now = datetime.now()
        
        # 检查日期是否变化（过了零点）
        if now.date() != self.current_date:
            # 新的一天，重置学习时长统计
            self.study_hours_count = 0
            self.current_date = now.date()
            self.study_hours_label.setText(f'📊 已学习: 0 小时')
            print(f'新的一天开始，学习时长已重置: {self.current_date}')
        
        elapsed = (now - self.start_time).total_seconds()
        total_seconds = self.interval_minutes * 60
        remaining_seconds = total_seconds - elapsed
        
        if remaining_seconds <= 0:
            # 时间到，打开视频
            self.open_random_video()
            
            # 增加学习小时计数
            self.study_hours_count += 1
            self.study_hours_label.setText(f'📊 已学习: {self.study_hours_count} 小时')
            
            # 显示飞书时长统计提醒
            self.show_feishu_reminder()
            
            # 重置计时器
            self.start_time = datetime.now()
            remaining_seconds = total_seconds
        
        # 计算剩余时间
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        # 更新显示
        self.time_label.setText(f'距离下次休息: {minutes:02d}:{seconds:02d}')
        
        # 更新进度条
        progress = int((elapsed / total_seconds) * 100)
        self.progress_bar.setValue(progress)
        
        # 更新电池状态
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
    
    def show_feishu_reminder(self):
        """显示飞书工作时长统计提醒"""
        self.tray_icon.showMessage(
            '📊 记录学习时长',
            f'你已经学习了 {self.study_hours_count} 小时！\n\n'
            '别忘了到飞书多维表格的\n'
            '【工作时长】当天统计里加 1 小时哦~',
            QSystemTrayIcon.Information,
            8000  # 显示8秒
        )
        
        # 如果窗口可见，也闪烁提醒
        if self.isVisible():
            # 让学习时长标签闪烁
            original_style = self.study_hours_label.styleSheet()
            flash_style = 'color: #FF6B6B; font-weight: bold; background-color: rgba(255, 215, 0, 50);'
            
            self.study_hours_label.setStyleSheet(flash_style)
            QTimer.singleShot(500, lambda: self.study_hours_label.setStyleSheet(original_style))
            QTimer.singleShot(1000, lambda: self.study_hours_label.setStyleSheet(flash_style))
            QTimer.singleShot(1500, lambda: self.study_hours_label.setStyleSheet(original_style))
            QTimer.singleShot(2000, lambda: self.study_hours_label.setStyleSheet(flash_style))
            QTimer.singleShot(2500, lambda: self.study_hours_label.setStyleSheet(original_style))
        
    def get_bilibili_videos(self):
        """
        获取B站收藏夹视频列表
        注意：由于B站API需要认证，这里提供一个简化版本
        实际使用时需要配置cookies或使用bilibili-api库
        """
        # 收藏夹ID
        fid = '3648313921'
        mid = '529362421'
        
        try:
            # 这是一个简化的实现，实际需要处理认证
            url = f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={fid}&pn=1&ps=20'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    medias = data.get('data', {}).get('medias', [])
                    videos = []
                    for media in medias:
                        bvid = media.get('bvid')
                        if bvid:
                            videos.append(f'https://www.bilibili.com/video/{bvid}')
                    return videos
        except Exception as e:
            print(f'获取视频列表失败: {e}')
        
        # 如果API调用失败，返回收藏夹页面
        return [f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create']
    
    def open_random_video(self):
        """打开随机视频"""
        # 获取视频列表
        if not self.video_list:
            self.video_list = self.get_bilibili_videos()
        
        if self.video_list:
            # 随机选择一个视频
            video_url = random.choice(self.video_list)
            print(f'打开视频: {video_url}')
            
            # 使用默认浏览器打开
            webbrowser.open(video_url)
            
            # 显示通知
            self.tray_icon.showMessage(
                '休息时间到！',
                '已为您打开休息视频，记得放松一下哦~',
                QSystemTrayIcon.Information,
                3000
            )
        else:
            # 如果获取失败，直接打开收藏夹页面
            fallback_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create'
            webbrowser.open(fallback_url)
            self.tray_icon.showMessage(
                '休息时间到！',
                '已为您打开收藏夹页面~',
                QSystemTrayIcon.Information,
                3000
            )
    
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
        self.tray_icon.hide()
        QApplication.quit()


def main():
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
    
    # 检查命令行参数，判断是否静默启动
    silent_start = '--silent' in sys.argv or '--startup' in sys.argv
    
    widget = RestReminderWidget(silent_start=silent_start)
    
    # 静默启动模式：直接隐藏窗口，只显示托盘图标
    if silent_start:
        widget.hide()
    else:
        widget.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
