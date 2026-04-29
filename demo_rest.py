"""
休息提醒演示版 - 10秒后触发休息提醒
"""
import sys
import webbrowser
import random
import requests
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                             QProgressBar, QSystemTrayIcon, QMenu, QAction, QHBoxLayout)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont
import psutil


class DemoWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.interval_seconds = 10  # 10秒后触发（演示用）
        self.start_time = datetime.now()
        self.video_list = []
        self.last_charging_state = None
        self.battery_warning_shown = False
        self.battery_notification_active = False  # 电池通知是否正在显示
        
        self.init_ui()
        self.center_on_screen()  # 居中显示
        self.init_tray()
        self.setup_timer()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle('休息提醒 - 演示模式')
        self.widget_width = 350
        self.widget_height = 220
        self.setGeometry(100, 100, self.widget_width, self.widget_height)
        
        # 设置窗口置顶
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(40, 40, 40, 230);
                border-radius: 10px;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                text-align: center;
                background-color: #333;
            }
            QProgressBar::chunk {
                background-color: #00AFF0;
                border-radius: 3px;
            }
            #battery_bar::chunk {
                background-color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 标题
        self.title_label = QLabel('⏰ 休息提醒 - 演示模式')
        self.title_label.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)
        
        # 演示说明
        demo_label = QLabel('⚡ 10秒后触发休息提醒')
        demo_label.setStyleSheet('color: #FFD700; font-size: 12px;')
        demo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(demo_label)
        
        # 时间显示
        self.time_label = QLabel('距离下次休息: 00:10')
        self.time_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.time_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat('%p%')
        layout.addWidget(self.progress_bar)
        
        # 电池状态
        battery_layout = QHBoxLayout()
        self.battery_label = QLabel('🔋 检测中...')
        self.battery_label.setFont(QFont('Microsoft YaHei', 11))
        battery_layout.addWidget(self.battery_label)
        layout.addLayout(battery_layout)
        
        # 电池电量进度条
        self.battery_bar = QProgressBar()
        self.battery_bar.setObjectName('battery_bar')
        self.battery_bar.setMaximum(100)
        self.battery_bar.setValue(0)
        self.battery_bar.setTextVisible(True)
        self.battery_bar.setFormat('%p%')
        self.battery_bar.setMaximumHeight(20)
        layout.addWidget(self.battery_bar)
        
        self.setLayout(layout)
    
    def center_on_screen(self):
        """居中显示"""
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.widget_width) // 2
        y = (screen.height() - self.widget_height) // 2
        self.move(x, y)
        
    def init_tray(self):
        """初始化系统托盘"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip('休息提醒 - 演示模式')
        
        tray_menu = QMenu()
        quit_action = QAction('退出', self)
        quit_action.triggered.connect(self.quit_app)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setIcon(self.style().standardIcon(self.style().SP_MessageBoxInformation))
        self.tray_icon.show()
        
    def setup_timer(self):
        """设置定时器"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(100)  # 每100毫秒更新一次（更流畅）
        
    def update_display(self):
        """更新显示内容"""
        now = datetime.now()
        elapsed = (now - self.start_time).total_seconds()
        remaining_seconds = self.interval_seconds - elapsed
        
        if remaining_seconds <= 0:
            # 时间到，触发休息提醒
            self.trigger_rest_reminder()
            # 重置计时器
            self.start_time = datetime.now()
            remaining_seconds = self.interval_seconds
        
        # 计算剩余时间
        minutes = int(remaining_seconds // 60)
        seconds = int(remaining_seconds % 60)
        
        # 更新显示
        self.time_label.setText(f'距离下次休息: {minutes:02d}:{seconds:02d}')
        
        # 更新进度条
        progress = int((elapsed / self.interval_seconds) * 100)
        self.progress_bar.setValue(progress)
        
        # 更新电池状态
        self.update_battery_status()
        
    def update_battery_status(self):
        """更新电池状态"""
        try:
            battery = psutil.sensors_battery()
            
            if battery is None:
                self.battery_label.setText('🖥️ 台式机（无电池）')
                self.battery_bar.setValue(100)
                return
            
            percent = battery.percent
            plugged = battery.power_plugged
            
            self.battery_bar.setValue(int(percent))
            
            if plugged:
                if percent >= 100:
                    self.battery_label.setText('🔌 已充满')
                else:
                    self.battery_label.setText('⚡ 充电中')
                
                # 重新充电后，关闭之前的断电警告
                if self.battery_notification_active:
                    self.tray_icon.showMessage('', '', QSystemTrayIcon.NoIcon, 1)
                    self.battery_notification_active = False
                
                # 重置警告状态
                self.battery_warning_shown = False
            else:
                if percent <= 20:
                    self.battery_label.setText('🪫 电量低')
                else:
                    self.battery_label.setText('🔋 使用电池')
                
                # 检测断电：只提醒一次
                if self.last_charging_state is True and not plugged:
                    if not self.battery_warning_shown:
                        self.tray_icon.showMessage(
                            '⚠️ 电源已断开',
                            f'当前电量: {percent}%\n建议连接电源',
                            QSystemTrayIcon.Warning,
                            5000
                        )
                        self.battery_warning_shown = True
                        self.battery_notification_active = True
            
            self.last_charging_state = plugged
        except:
            self.battery_label.setText('❌ 电池状态获取失败')
    
    def trigger_rest_reminder(self):
        """触发休息提醒"""
        print("\n" + "=" * 60)
        print("🎉 休息时间到！")
        print("=" * 60)
        
        # 1. 显示系统通知
        self.tray_icon.showMessage(
            '⏰ 休息时间到！',
            '已经工作了一段时间，该休息一下了！\n正在为您打开休息视频...',
            QSystemTrayIcon.Information,
            5000
        )
        
        # 2. 窗口闪烁提醒
        self.flash_window()
        
        # 3. 打开视频
        self.open_random_video()
        
    def flash_window(self):
        """窗口闪烁提醒"""
        if self.isVisible():
            # 闪烁3次
            for i in range(3):
                QTimer.singleShot(i * 400, lambda: self.setWindowOpacity(0.3))
                QTimer.singleShot(i * 400 + 200, lambda: self.setWindowOpacity(1.0))
    
    def get_bilibili_videos(self):
        """获取B站收藏夹视频列表"""
        fid = '3648313921'
        mid = '529362421'
        
        try:
            url = f'https://api.bilibili.com/x/v3/fav/resource/list?media_id={fid}&pn=1&ps=20'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Referer': 'https://www.bilibili.com'
            }
            
            response = requests.get(url, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('code') == 0:
                    medias = data.get('data', {}).get('medias', [])
                    videos = []
                    for media in medias:
                        bvid = media.get('bvid')
                        title = media.get('title', '未知标题')
                        if bvid:
                            videos.append({
                                'url': f'https://www.bilibili.com/video/{bvid}',
                                'title': title
                            })
                    return videos
        except Exception as e:
            print(f'获取视频列表失败: {e}')
        
        return []
    
    def open_random_video(self):
        """打开随机视频"""
        print("\n正在获取视频列表...")
        
        if not self.video_list:
            self.video_list = self.get_bilibili_videos()
        
        if self.video_list:
            # 随机选择一个视频
            video = random.choice(self.video_list)
            video_url = video['url']
            video_title = video['title']
            
            print(f"✓ 随机选择视频: {video_title}")
            print(f"✓ 视频链接: {video_url}")
            print(f"✓ 正在用默认浏览器打开...")
            
            # 使用默认浏览器打开
            webbrowser.open(video_url)
            
            print("✓ 视频已打开！")
        else:
            # 如果获取失败，直接打开收藏夹页面
            fallback_url = 'https://space.bilibili.com/529362421/favlist?fid=3648313921&ftype=create'
            print(f"✓ 打开收藏夹页面: {fallback_url}")
            webbrowser.open(fallback_url)
        
        print("=" * 60)
        print()
    
    def quit_app(self):
        """退出应用"""
        self.tray_icon.hide()
        QApplication.quit()


def main():
    print("=" * 60)
    print("休息提醒 - 演示模式")
    print("=" * 60)
    print()
    print("⚡ 演示设置：10秒后触发休息提醒")
    print()
    print("当时间到达时，程序会：")
    print("  1. 显示系统通知")
    print("  2. 窗口闪烁提醒")
    print("  3. 自动打开B站收藏夹中的随机视频")
    print()
    print("=" * 60)
    print()
    
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    widget = DemoWidget()
    widget.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
