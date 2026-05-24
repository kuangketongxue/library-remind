"""预览：小型浮窗倒计时（拖动 + 位置记忆 + 进度条 + 呼吸动画 + 音效）"""
import sys, os, json, time, math
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, Qt, QPoint
import winsound

POS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.overlay_pos.json')


class DemoOverlay(QWidget):
    def __init__(self):
        super().__init__()
        self.remaining = 300
        self._total = 300

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(200, 110)
        self.setCursor(Qt.OpenHandCursor)
        self.setStyleSheet("""
            background-color: rgba(30, 30, 30, 210);
            border-radius: 12px;
            border: 1px solid rgba(255, 217, 61, 0.15);
        """)

        self._drag_offset = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 8)
        layout.setSpacing(2)

        self.title = QLabel('📚 学习即将结束')
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet('color: #FFD93D; font-size: 12px; font-weight: bold; background: transparent; border: none;')

        self.timer_label = QLabel('05:00')
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.timer_label.setStyleSheet('color: #FFFFFF; font-size: 36px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')

        self.hint = QLabel('准备休息一下~')
        self.hint.setAlignment(Qt.AlignCenter)
        self.hint.setStyleSheet('color: #999; font-size: 11px; background: transparent; border: none;')

        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        self.progress.setValue(100)
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar { background: rgba(255,255,255,0.06); border: none; border-radius: 2px; }
            QProgressBar::chunk { background: qlineargradient(x1:0, x2:1, stop:0 #788C57, stop:0.6 #FFD93D, stop:1 #FF6B50); border-radius: 2px; }
        """)

        layout.addWidget(self.title)
        layout.addWidget(self.timer_label)
        layout.addWidget(self.hint)
        layout.addWidget(self.progress)

        # 定位
        try:
            if os.path.exists(POS_FILE):
                with open(POS_FILE, 'r') as f:
                    pos = json.load(f)
                self.move(QPoint(pos['x'], pos['y']))
            else:
                raise FileNotFoundError
        except Exception:
            screen = QApplication.primaryScreen()
            if screen:
                g = screen.geometry()
                self.move(g.width() - 220, 30)

        self.show()

        try:
            winsound.Beep(880, 150)
            winsound.Beep(1100, 200)
        except Exception:
            pass

        self.t = QTimer()
        self.t.timeout.connect(self.tick)
        self.t.start(1000)

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
        try:
            p = self.frameGeometry().topLeft()
            with open(POS_FILE, 'w') as f:
                json.dump({'x': p.x(), 'y': p.y()}, f)
        except Exception:
            pass

    def tick(self):
        self.remaining -= 1
        if self.remaining <= 0:
            self.title.setText('🎉 休息时间到！')
            self.timer_label.setText('00:00')
            self.timer_label.setStyleSheet('color: #96aa72; font-size: 36px; font-weight: bold; font-family: Consolas; background: transparent; border: none;')
            self.hint.setText('已打开 B 站视频')
            self.progress.setValue(0)
            self.t.stop()
            QTimer.singleShot(3000, QApplication.quit)
            return

        m = self.remaining // 60
        s = self.remaining % 60
        self.timer_label.setText(f'{m:02d}:{s:02d}')
        self.progress.setValue(int((self.remaining / self._total) * 100))

        if self.remaining <= 60:
            phase = math.sin(time.time() * 3)
            font_size = int(36 + phase * 3)
            color = '#FF8A70' if phase > 0 else '#FF6B50'
            self.timer_label.setStyleSheet(
                f'color: {color}; font-size: {font_size}px; font-weight: bold; font-family: Consolas; background: transparent; border: none;'
            )
            self.title.setStyleSheet('color: #FF6B50; font-size: 12px; font-weight: bold; background: transparent; border: none;')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = DemoOverlay()
    print('[预览] 小型浮窗倒计时 — 拖动移动 | 位置记忆 | 进度条 | 呼吸动画 | 音效')
    sys.exit(app.exec_())
