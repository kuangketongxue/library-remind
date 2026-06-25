"""最小托盘图标测试 — 验证系统托盘是否可用"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt

app = QApplication([])

# 检查托盘是否可用
print(f'System tray available: {QSystemTrayIcon.isSystemTrayAvailable()}')

# 动态生成图标
pm = QPixmap(64, 64)
pm.fill(Qt.transparent)
p = QPainter(pm)
p.setRenderHint(QPainter.Antialiasing)
p.setBrush(QBrush(QColor(212, 175, 55, 30)))
p.setPen(Qt.NoPen)
p.drawEllipse(2, 2, 60, 60)
p.setBrush(QBrush(QColor(20, 20, 24)))
p.setPen(QPen(QColor(212, 175, 55, 120), 2))
p.drawEllipse(6, 6, 52, 52)
p.setPen(QColor(212, 175, 55))
p.setFont(QFont('Segoe UI Emoji', 20, QFont.Bold))
p.drawText(pm.rect(), Qt.AlignCenter, '⚡')
p.end()

icon = QIcon(pm)
print(f'Icon isNull: {icon.isNull()}')

# 创建托盘图标
tray = QSystemTrayIcon(icon)
tray.setToolTip('测试图标')

menu = QMenu()
menu.addAction('测试菜单项')
tray.setContextMenu(menu)

tray.show()
print(f'Tray visible: {tray.isVisible()}')

# 5秒后自动退出
from PyQt5.QtCore import QTimer
QTimer.singleShot(5000, app.quit)
app.exec_()
print('Done')
