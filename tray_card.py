"""
自定义托盘卡片 — 替代原生 QMenu
深色奢华风格，2列布局：今日概览 + 功能菜单
"""
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame, QApplication, QSystemTrayIcon)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal, QPoint, QEvent
from PyQt5.QtGui import QFont, QPainter, QColor, QBrush, QPen, QPainterPath


class ClickableRow(QFrame):
    """可点击的行 QFrame，整行点击触发 callback，不破坏子控件原生事件"""
    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self._callback = callback
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            ClickableRow { background: transparent; border: none; border-radius: 6px; }
            ClickableRow:hover { background: rgba(255,255,255,0.03); }
        """)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(8, 6, 8, 6)
        self._layout.setSpacing(10)

    def layout(self):
        return self._layout

    def mousePressEvent(self, event):
        self._callback()
        super().mousePressEvent(event)


class TrayCardWidget(QWidget):
    """可浮动托盘卡片 — 替代原生右键菜单"""

    action_requested = pyqtSignal(str)

    CARD_WIDTH = 360
    CARD_HEIGHT = 420

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.Popup |
            Qt.FramelessWindowHint |
            Qt.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)

        # Data (set externally before show)
        self.study_hours = 0
        self.streak = 0
        self.break_minutes = 0
        self.autostart_enabled = False
        self.reminder_mode = 'video'
        self.version = 'v3.3'

        self._fade_anim = None
        self._build_ui()

    # ── UI 构建 ──

    def _build_ui(self):
        self._root = QFrame(self)
        self._root.setGeometry(4, 4, self.CARD_WIDTH - 8, self.CARD_HEIGHT - 8)
        self._root.setObjectName('cardRoot')
        self._root.setStyleSheet("""
            QFrame#cardRoot {
                background-color: #0e0e16;
                border: 1px solid rgba(212, 175, 55, 0.10);
                border-radius: 18px;
            }
        """)

        layout = QVBoxLayout(self._root)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(0)

        # ── Header ──
        header = QHBoxLayout()
        brand = QLabel('⚡ 精力管理')
        brand.setFont(QFont('Microsoft YaHei', 12, QFont.Bold))
        brand.setStyleSheet('color: #d4af37; background: transparent;')
        header.addWidget(brand)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(12)

        # ── Overview Stats ──
        self._stat_widgets = {}
        stats_row = QHBoxLayout()
        stats_row.setSpacing(8)
        for key, label, color, _default in [
            ('study', '今日学习', 'gold', '0h'),
            ('streak', '连续打卡', 'orange', '0'),
            ('break', '今日休息', 'green', '0m'),
        ]:
            frame = QFrame()
            frame.setStyleSheet('background: rgba(255,255,255,0.015); border: 1px solid rgba(255,255,255,0.03); border-radius: 10px;')
            col = QVBoxLayout(frame)
            col.setContentsMargins(8, 8, 8, 8)
            col.setSpacing(2)
            val = QLabel(_default)
            val.setAlignment(Qt.AlignCenter)
            val.setFont(QFont('Consolas', 16, QFont.Bold))
            color_map = {'gold': '#d4af37', 'orange': '#d97757', 'green': '#6a9b6a'}
            val.setStyleSheet(f'color: {color_map[color]}; background: transparent;')
            val.setObjectName(f'stat_{key}')
            lbl = QLabel(label)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setFont(QFont('Microsoft YaHei', 8))
            lbl.setStyleSheet('color: #666; background: transparent;')
            col.addWidget(val)
            col.addWidget(lbl)
            stats_row.addWidget(frame)
            self._stat_widgets[key] = val
        layout.addLayout(stats_row)

        # ── Separator ──
        layout.addSpacing(10)
        sep1 = QFrame()
        sep1.setFixedHeight(1)
        sep1.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.2 rgba(212,175,55,0.06), stop:0.8 rgba(212,175,55,0.06), stop:1 transparent); border: none;')
        layout.addWidget(sep1)
        layout.addSpacing(4)

        # ── Menu Items ──
        self._mode_chips = {}
        mode_map = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '通知', 'none': '无操作'}

        for icon, title, action_name in [
            ('🎯', '设定今日目标', 'set_goal'),
            ('👁', '显示/隐藏窗口', 'toggle_visibility'),
            ('🔁', '开机自启动', 'toggle_autostart'),
            ('🔔', '提醒方式', 'reminder_mode'),
            ('📊', '学习统计', 'show_stats'),
            ('📋', '导出本周数据', 'export_data'),
        ]:
            if action_name == 'toggle_autostart':
                # 可点击整行
                row = ClickableRow(lambda: self.action_requested.emit('toggle_autostart'))
                rl = row.layout()
                icon_lbl = self._make_icon(icon)
                rl.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #e8e6e1; background: transparent;')
                col.addWidget(t)
                desc = QLabel('系统登录后自动运行')
                desc.setFont(QFont('Microsoft YaHei', 8))
                desc.setStyleSheet('color: #666; background: transparent;')
                col.addWidget(desc)
                rl.addLayout(col)
                rl.addStretch()
                self._toggle_frame = QFrame()
                self._toggle_frame.setFixedSize(34, 18)
                self._toggle_frame.setObjectName('toggleWidget')
                self._toggle_frame.setStyleSheet(self._toggle_style(self.autostart_enabled))
                rl.addWidget(self._toggle_frame)
                layout.addWidget(row)
                layout.addSpacing(2)

            elif action_name == 'reminder_mode':
                # 提醒方式 + chip row（不可点击整行，chip可点）
                row_hint = QHBoxLayout()
                row_hint.setSpacing(10)
                icon_lbl = self._make_icon(icon)
                row_hint.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #e8e6e1; background: transparent;')
                col.addWidget(t)
                self._mode_label = QLabel(mode_map.get(self.reminder_mode, ''))
                self._mode_label.setFont(QFont('Microsoft YaHei', 8))
                self._mode_label.setStyleSheet('color: #d4af37; background: transparent;')
                col.addWidget(self._mode_label)
                row_hint.addLayout(col)
                row_hint.addStretch()
                layout.addLayout(row_hint)

                # Chips
                chips_layout = QHBoxLayout()
                chips_layout.setSpacing(4)
                chips_layout.setContentsMargins(42, 0, 0, 6)
                for mode_key, mode_lbl in mode_map.items():
                    chip = QPushButton(mode_lbl)
                    chip.setFont(QFont('Microsoft YaHei', 8))
                    chip.setFixedHeight(22)
                    chip.setCursor(Qt.PointingHandCursor)
                    is_active = mode_key == self.reminder_mode
                    chip.setStyleSheet(self._chip_style(is_active))
                    chip.clicked.connect(lambda checked, k=mode_key: self.action_requested.emit(f'set_mode:{k}'))
                    chips_layout.addWidget(chip)
                    self._mode_chips[mode_key] = chip
                layout.addLayout(chips_layout)
                layout.addSpacing(2)

            elif action_name == 'show_stats':
                sep_light = QFrame()
                sep_light.setFixedHeight(1)
                sep_light.setStyleSheet('background: rgba(255,255,255,0.02); border: none;')
                layout.addWidget(sep_light)
                layout.addSpacing(4)

                row = ClickableRow(lambda: self.action_requested.emit(action_name))
                rl = row.layout()
                icon_lbl = self._make_icon(icon)
                rl.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #e8e6e1; background: transparent;')
                col.addWidget(t)
                desc = QLabel('最近7天学习趋势图表')
                desc.setFont(QFont('Microsoft YaHei', 8))
                desc.setStyleSheet('color: #666; background: transparent;')
                col.addWidget(desc)
                rl.addLayout(col)
                rl.addStretch()
                arrow = QLabel('↗')
                arrow.setStyleSheet('color: #555; font-size: 12px; background: transparent;')
                rl.addWidget(arrow)
                layout.addWidget(row)
                layout.addSpacing(2)

            elif action_name == 'export_data':
                row = ClickableRow(lambda: self.action_requested.emit(action_name))
                rl = row.layout()
                icon_lbl = self._make_icon(icon)
                rl.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #e8e6e1; background: transparent;')
                col.addWidget(t)
                desc = QLabel('复制本周数据到剪贴板')
                desc.setFont(QFont('Microsoft YaHei', 8))
                desc.setStyleSheet('color: #666; background: transparent;')
                col.addWidget(desc)
                rl.addLayout(col)
                rl.addStretch()
                hint = QLabel('⌘C')
                hint.setFont(QFont('Consolas', 8))
                hint.setStyleSheet('color: #555; background: transparent;')
                rl.addWidget(hint)
                layout.addWidget(row)
                layout.addSpacing(2)

            elif action_name == 'set_goal':
                row = ClickableRow(lambda: self.action_requested.emit(action_name))
                rl = row.layout()
                icon_lbl = self._make_icon(icon)
                rl.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #d4af37; background: transparent;')
                col.addWidget(t)
                desc = QLabel('重新设定今日学习目标')
                desc.setFont(QFont('Microsoft YaHei', 8))
                desc.setStyleSheet('color: #888; background: transparent;')
                col.addWidget(desc)
                rl.addLayout(col)
                rl.addStretch()
                arrow = QLabel('↗')
                arrow.setStyleSheet('color: #d4af37; font-size: 12px; background: transparent;')
                rl.addWidget(arrow)
                layout.addWidget(row)
                layout.addSpacing(2)

            else:  # toggle_visibility
                row = ClickableRow(lambda: self.action_requested.emit(action_name))
                rl = row.layout()
                icon_lbl = self._make_icon(icon)
                rl.addWidget(icon_lbl)
                col = QVBoxLayout()
                col.setSpacing(1)
                t = QLabel(title)
                t.setFont(QFont('Microsoft YaHei', 10, QFont.Bold))
                t.setStyleSheet('color: #e8e6e1; background: transparent;')
                col.addWidget(t)
                desc = QLabel('Ctrl+Alt+P')
                desc.setFont(QFont('Microsoft YaHei', 8))
                desc.setStyleSheet('color: #666; background: transparent;')
                col.addWidget(desc)
                rl.addLayout(col)
                rl.addStretch()
                layout.addWidget(row)
                layout.addSpacing(2)

        layout.addStretch()

        # ── Separator + Footer ──
        sep2 = QFrame()
        sep2.setFixedHeight(1)
        sep2.setStyleSheet('background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 transparent, stop:0.2 rgba(212,175,55,0.06), stop:0.8 rgba(212,175,55,0.06), stop:1 transparent); border: none;')
        layout.addWidget(sep2)
        layout.addSpacing(6)

        footer = QHBoxLayout()
        ver = QLabel(self.version)
        ver.setFont(QFont('Consolas', 8))
        ver.setStyleSheet('color: #444; background: transparent;')
        footer.addWidget(ver)
        footer.addStretch()
        tip = QLabel('⏎ 点击即执行')
        tip.setFont(QFont('Microsoft YaHei', 8))
        tip.setStyleSheet('color: #444; background: transparent;')
        footer.addWidget(tip)
        layout.addLayout(footer)

        # 退出按钮
        quit_layout = QHBoxLayout()
        quit_layout.setContentsMargins(42, 4, 0, 0)
        quit_btn = QPushButton('⏻  退出程序')
        quit_btn.setFont(QFont('Microsoft YaHei', 9))
        quit_btn.setCursor(Qt.PointingHandCursor)
        quit_btn.setStyleSheet("""
            QPushButton {
                color: #d95757; background: rgba(217,87,87,0.06);
                border: 1px solid rgba(217,87,87,0.10);
                border-radius: 6px; padding: 4px 10px;
            }
            QPushButton:hover {
                background: rgba(217,87,87,0.12);
            }
        """)
        quit_btn.clicked.connect(lambda: self.action_requested.emit('quit_app'))
        quit_layout.addStretch()
        quit_layout.addWidget(quit_btn)
        layout.addLayout(quit_layout)

    # ── 辅助方法 ──

    def _make_icon(self, emoji):
        lbl = QLabel(emoji)
        lbl.setFixedSize(30, 30)
        lbl.setAlignment(Qt.AlignCenter)
        lbl.setFont(QFont('Segoe UI Emoji', 14))
        lbl.setStyleSheet("""
            background: rgba(255,255,255,0.02);
            border: 1px solid rgba(255,255,255,0.03);
            border-radius: 7px;
        """)
        return lbl

    def _toggle_style(self, enabled):
        if enabled:
            return """
                QFrame#toggleWidget {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #2a5a20, stop:0.6 #3a7a30, stop:1 #4a9a40);
                    border: 1px solid #5aaa50; border-radius: 9px;
                }
            """
        return """
            QFrame#toggleWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2a2a28, stop:0.6 #3a3a38, stop:1 #444);
                border: 1px solid #555; border-radius: 9px;
            }
        """

    def _chip_style(self, active):
        if active:
            return """
                QPushButton {
                    color: #d4af37; background: rgba(212,175,55,0.10);
                    border: 1px solid rgba(212,175,55,0.15);
                    border-radius: 5px; padding: 2px 8px;
                }
                QPushButton:hover { background: rgba(212,175,55,0.18); }
            """
        return """
            QPushButton {
                color: #666; background: transparent;
                border: 1px solid rgba(255,255,255,0.04);
                border-radius: 5px; padding: 2px 8px;
            }
            QPushButton:hover { color: #999; border-color: rgba(255,255,255,0.08); }
        """

    # ── 数据更新 ──

    def update_data(self, **kwargs):
        if 'study_hours' in kwargs:
            self._stat_widgets['study'].setText(f'{kwargs["study_hours"]}h')
        if 'streak' in kwargs:
            self._stat_widgets['streak'].setText(str(kwargs['streak']))
        if 'break_minutes' in kwargs:
            self._stat_widgets['break'].setText(f'{kwargs["break_minutes"]}m')
        if 'autostart' in kwargs:
            self.autostart_enabled = kwargs['autostart']
            if hasattr(self, '_toggle_frame'):
                self._toggle_frame.setStyleSheet(self._toggle_style(self.autostart_enabled))
        if 'reminder_mode' in kwargs:
            self.reminder_mode = kwargs['reminder_mode']
            mode_names = {'video': '打开B站', 'quote': '💡 请辨金句', 'notify': '通知', 'none': '无操作'}
            if hasattr(self, '_mode_label'):
                self._mode_label.setText(mode_names.get(kwargs['reminder_mode'], ''))
            for key, chip in getattr(self, '_mode_chips', {}).items():
                chip.setStyleSheet(self._chip_style(key == kwargs['reminder_mode']))

    # ── 显示/隐藏 ──

    def show_at(self, pos: QPoint):
        screen = QApplication.primaryScreen()
        if screen:
            sg = screen.geometry()
            x = min(pos.x(), sg.width() - self.CARD_WIDTH - 8)
            y = min(pos.y() - self.CARD_HEIGHT - 8, sg.height() - self.CARD_HEIGHT - 8)
            y = max(y, 20)
            self.move(x, y)
        else:
            self.move(pos.x() - self.CARD_WIDTH + 50, pos.y() - self.CARD_HEIGHT - 10)
        self.show()
        self.raise_()
        self.activateWindow()

    # ── Paint: drop shadow ──

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QBrush(QColor(0, 0, 0, 60)))
        painter.setPen(Qt.NoPen)
        path = QPainterPath()
        path.addRoundedRect(8, 6, self.CARD_WIDTH - 16, self.CARD_HEIGHT - 12, 18, 18)
        painter.drawPath(path)

        painter.setBrush(QBrush(QColor(0, 0, 0, 30)))
        path = QPainterPath()
        path.addRoundedRect(4, 2, self.CARD_WIDTH - 8, self.CARD_HEIGHT - 6, 18, 18)
        painter.drawPath(path)