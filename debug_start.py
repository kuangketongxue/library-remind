"""
调试启动脚本 - 显示详细信息
"""
import sys
import os

print("=" * 60)
print("休息提醒挂件 - 调试启动")
print("=" * 60)
print()

# 检查依赖
print("[1/5] 检查依赖...")
try:
    from PyQt5.QtWidgets import QApplication
    print("  ✓ PyQt5.QtWidgets")
except Exception as e:
    print(f"  ✗ PyQt5.QtWidgets: {e}")
    sys.exit(1)

try:
    import psutil
    print("  ✓ psutil")
except Exception as e:
    print(f"  ✗ psutil: {e}")
    sys.exit(1)

try:
    import requests
    print("  ✓ requests")
except Exception as e:
    print(f"  ✗ requests: {e}")
    sys.exit(1)

print()

# 检查文件
print("[2/5] 检查文件...")
if os.path.exists('rest_reminder.py'):
    print("  ✓ rest_reminder.py 存在")
else:
    print("  ✗ rest_reminder.py 不存在")
    sys.exit(1)

print()

# 导入主程序
print("[3/5] 导入主程序...")
try:
    from rest_reminder import RestReminderWidget
    print("  ✓ 主程序导入成功")
except Exception as e:
    print(f"  ✗ 导入失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 创建应用
print("[4/5] 创建应用...")
try:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    print("  ✓ QApplication 创建成功")
except Exception as e:
    print(f"  ✗ 创建失败: {e}")
    sys.exit(1)

print()

# 创建窗口
print("[5/5] 创建窗口...")
try:
    widget = RestReminderWidget(silent_start=False)
    print("  ✓ 窗口对象创建成功")
    print(f"  窗口大小: {widget.width()} x {widget.height()}")
    print(f"  窗口位置: ({widget.x()}, {widget.y()})")
except Exception as e:
    print(f"  ✗ 创建失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("准备显示窗口...")
print("=" * 60)
print()
print("窗口应该显示在屏幕右侧")
print("如果看不到，请检查：")
print("  1. 屏幕右侧边缘")
print("  2. 系统托盘图标")
print("  3. 任务栏是否有程序")
print()

# 显示窗口
widget.show()
print("✓ 窗口已调用 show() 方法")
print()

# 运行应用
print("启动事件循环...")
sys.exit(app.exec_())
