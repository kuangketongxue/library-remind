"""
最简单的窗口测试
"""
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt

print("正在创建窗口...")

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle('测试窗口 - 你能看到我吗？')
window.setGeometry(500, 300, 500, 300)
window.setWindowFlags(Qt.WindowStaysOnTopHint)

layout = QVBoxLayout()
label = QLabel('🎉 如果你能看到这个窗口\n说明程序可以正常运行！\n\n窗口位置：屏幕中央\n窗口大小：500x300')
label.setStyleSheet('font-size: 20px; padding: 50px;')
label.setAlignment(Qt.AlignCenter)
layout.addWidget(label)

window.setLayout(layout)
window.show()

print("窗口已显示！")
print("窗口位置:", window.x(), window.y())
print("窗口大小:", window.width(), window.height())
print("如果看不到窗口，请检查：")
print("1. 是否被其他窗口遮挡")
print("2. 是否在其他显示器上")
print("3. 任务栏是否有程序图标")

sys.exit(app.exec_())
