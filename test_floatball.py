
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
import sys

class FloatingBall(QWidget):
    def __init__(self):
        super().__init__()
        self.dragging = False
        self.drag_position = None
        
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | 
            Qt.FramelessWindowHint | 
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(60, 60)
        
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(120, 140, 87)
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(Qt.NoPen))
        painter.drawEllipse(0, 0, 60, 60)
        painter.setPen(QColor(250, 249, 245))
        painter.setFont(QFont('Arial', 20, QFont.Bold))
        painter.drawText(self.rect(), Qt.AlignCenter, '⏰')

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if self.dragging and self.drag_position is not None:
            self.move(event.globalPos() - self.drag_position)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

if __name__ == '__main__':
    app = QApplication(sys.argv)
    fb = FloatingBall()
    sys.exit(app.exec_())
