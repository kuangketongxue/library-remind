# -*- coding: utf-8 -*-
"""Local font-rendering smoke test for 休息提醒.
Drop into app folder and run with the same Python that runs RestReminder.exe.
Shows a QFont legality report and a live sample window."""
import sys
seen = set()
def O(msg):
    if msg not in seen:
        print(msg, file=sys.stderr, flush=True)
        seen.add(msg)

try:
    from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout, QPushButton
    from PyQt5.QtGui import QFont, QFontDatabase
    from PyQt5.QtCore import Qt
except Exception as e:
    O(f"[FAIL] PyQt5 import: {e}"); sys.exit(2)

app = QApplication.instance() or QApplication(sys.argv)
db = QFontDatabase()

# ── Font legality checks (the bug we just fixed) ──
print("=" * 50, file=sys.stderr)
print("QFont LEGALITY CHECK", file=sys.stderr)
print("=" * 50, file=sys.stderr)
cases = [
    ("Georgia (fixed)",       "Georgia",                      20, False),
    ("Microsoft YaHei (fixed)","Microsoft YaHei",            11, False),
    ("Consolas (fixed)",      "Consolas",                    22, True),
    ("Segoe UI Emoji",        "Segoe UI Emoji",              14, False),
    ("BROKEN (old CSS str)",  'Georgia, "Noto Serif SC", serif', 20, False),
]
for name, fam, sz, bold in cases:
    f = QFont(fam, sz, QFont.Bold if bold else QFont.Normal)
    exact = db.exactMatch()
    actual_family = f.family()
    ok = (actual_family == fam)
    flag = "OK" if ok else "WRONG"
    O(f"  [{flag}] {name:<25} → family={actual_family!r}  exact={exact}")
O("")

# ── Live rendering sample ──
print("=" * 50, file=sys.stderr)
print("LIVE RENDER SAMPLE (press x to close)", file=sys.stderr)
print("=" * 50, file=sys.stderr)
w = QWidget()
w.setWindowTitle("休息提醒 · 字体测试")
w.resize(360, 220)
v = QVBoxLayout(w)
samples = [
    ("Georgia (主标题)",     "Georgia",             18, "#d4af37", "今日学习目标 · Daily Goal"),
    ("Consolas (倒计时)",    "Consolas",            24, "#6a9b6a", "25:00"),
    ("Microsoft YaHei",      "Microsoft YaHei",     11, "#e8e6e1", "耐心本身就是门槛 · 连续打卡 7 天"),
    ("Segoe UI Emoji",       "Segoe UI Emoji",      22, "#999",    "⚡ 👁️ 📊 🎯"),
]
for label_text, fam, sz, color, content in samples:
    hdr = QLabel(label_text)
    hdr.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))
    hdr.setStyleSheet("color: #777;")
    v.addWidget(hdr)
    lbl = QLabel(content)
    lbl.setFont(QFont(fam, sz))
    lbl.setStyleSheet(f"color: {color}; padding: 2px 6px;")
    v.addWidget(lbl)
v.addStretch()
btn = QPushButton("关闭测试")
btn.clicked.connect(w.close)
btn.setFont(QFont("Microsoft YaHei", 9))
v.addWidget(btn, 0, Qt.AlignRight)
w.show()
sys.exit(app.exec_() if app is not None else 0)
