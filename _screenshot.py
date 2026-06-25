"""截图测试 — 用 mss (DirectX) 截图，看能否看到用户桌面"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'vendor'))

import mss
import mss.tools

OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_desktop_screenshot.png')

with mss.mss() as sct:
    monitor = sct.monitors[1]  # 主显示器（monitors[0] = all）
    print(f"Monitor: {monitor}")
    screenshot = sct.grab(monitor)
    mss.tools.to_png(screenshot.rgb, screenshot.size, output=OUTPUT)
    print(f"Screenshot saved: {OUTPUT} ({screenshot.width}x{screenshot.height})")
