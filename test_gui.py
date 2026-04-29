"""
GUI测试版本 - 窗口显示在屏幕中央，更容易看到
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('休息提醒 - 测试窗口')
        self.setGeometry(100, 100, 400, 300)
        
        # 设置窗口置顶
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        # 设置样式
        self.setStyleSheet("""
            QWidget {
                background-color: #2C3E50;
                color: white;
            }
            QLabel {
                color: white;
                font-size: 16px;
                padding: 10px;
            }
            QPushButton {
                background-color: #3498DB;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980B9;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 标题
        title = QLabel('🎉 休息提醒挂件测试')
        title.setFont(QFont('Microsoft YaHei', 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 说明
        info = QLabel(
            '✅ PyQt5 安装成功！\n'
            '✅ GUI 窗口可以正常显示\n'
            '✅ 程序功能正常\n\n'
            '如果你能看到这个窗口，\n'
            '说明程序可以正常运行了！'
        )
        info.setAlignment(Qt.AlignCenter)
        layout.addWidget(info)
        
        # 按钮
        btn = QPushButton('启动完整版挂件')
        btn.clicked.connect(self.launch_full_version)
        layout.addWidget(btn)
        
        close_btn = QPushButton('关闭测试窗口')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        
        # 移动到屏幕中央
        self.center_on_screen()
        
    def center_on_screen(self):
        """将窗口移动到屏幕中央"""
        screen = QApplication.desktop().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
    
    def launch_full_version(self):
        """启动完整版"""
        import subprocess
        subprocess.Popen(['python', 'rest_reminder.py'])
        self.close()

def main():
    app = QApplication(sys.argv)
    widget = TestWidget()
    widget.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
