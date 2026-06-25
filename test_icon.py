import sys
sys.path.insert(0, r'C:\Users\binlo\Desktop\休息提醒\vendor')
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QPainter, QColor, QBrush, QPen, QFont, QIcon
from PyQt5.QtCore import Qt

def _create_app_icon(size=64):
    pm = QPixmap(size, size)
    pm.fill(Qt.transparent)
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QBrush(QColor(212, 175, 55, 30)))
    painter.setPen(Qt.NoPen)
    painter.drawEllipse(2, 2, size - 4, size - 4)
    painter.setBrush(QBrush(QColor(20, 20, 24)))
    painter.setPen(QPen(QColor(212, 175, 55, 120), 2))
    painter.drawEllipse(6, 6, size - 12, size - 12)
    painter.setPen(QColor(212, 175, 55))
    font_size = max(size // 3, 12)
    painter.setFont(QFont('Segoe UI Emoji', font_size, QFont.Bold))
    painter.drawText(pm.rect(), Qt.AlignCenter, '⚡')
    painter.end()
    icon = QIcon(pm)
    icon.addPixmap(pm.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation), QIcon.Normal, QIcon.Off)
    icon.addPixmap(pm.scaled(16, 16, Qt.KeepAspectRatio, Qt.SmoothTransformation), QIcon.Normal, QIcon.On)
    return icon

app = QApplication([])
icon = _create_app_icon()
print(f'isNull: {icon.isNull()}')
print('SUCCESS: Icon generated dynamically')
app.quit()
