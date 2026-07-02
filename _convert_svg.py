import sys
sys.path.insert(0, r'C:\Users\binlo\Desktop\休息提醒')
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QColor
from PyQt5.QtCore import Qt

svg_path = r'C:\Users\binlo\Desktop\github-icon.svg'
output_path = r'C:\Users\binlo\Desktop\github-icon.png'

pm = QPixmap(32, 32)
pm.fill(Qt.transparent)
painter = QPainter(pm)
painter.setRenderHint(QPainter.Antialiasing)
renderer = QSvgRenderer(svg_path)
renderer.render(painter)
painter.end()

pm.save(output_path)
print(f'Saved to {output_path}')
