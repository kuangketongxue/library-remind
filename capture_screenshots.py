"""截图脚本：启动应用，截取主界面 3 个 tab，保存到 screenshots/
用法：C:\\Python314\\python.exe capture_screenshots.py
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'vendor'))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import rest_reminder

app = QApplication(sys.argv)
widget = rest_reminder.RestReminderWidget(silent_start=False)
widget.show()

tabs = [('今日', '01-today'), ('AI 报告', '02-ai-report'), ('趋势', '03-trend')]
idx = [0]

def dismiss_popups():
    """关掉启动时弹出的对话框/浮球，避免干扰截图"""
    for w in app.topLevelWidgets():
        if w is not widget and w.isVisible():
            try:
                w.close()
            except Exception:
                pass
    # 隐藏浮球
    if hasattr(widget, 'ball') and widget.ball:
        widget.ball.hide()

def shoot_next():
    if idx[0] >= len(tabs):
        print('all screenshots done')
        app.quit()
        return
    tab_name, file_name = tabs[idx[0]]
    widget._switch_tab(tab_name)
    def capture():
        os.makedirs('screenshots', exist_ok=True)
        pix = widget.grab()
        path = os.path.join('screenshots', f'{file_name}.png')
        pix.save(path)
        print(f'saved {path}  ({pix.width()}x{pix.height()})')
        idx[0] += 1
        QTimer.singleShot(300, shoot_next)
    QTimer.singleShot(1000, capture)

QTimer.singleShot(1500, dismiss_popups)
QTimer.singleShot(2500, shoot_next)

sys.exit(app.exec_())
