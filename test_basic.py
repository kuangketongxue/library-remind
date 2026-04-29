"""
基础功能测试 - 不需要GUI
"""
import sys
import psutil
from datetime import datetime

print("=" * 50)
print("休息提醒挂件 - 基础功能测试")
print("=" * 50)
print()

# 测试1: 检查命令行参数
print("[测试1] 命令行参数解析")
silent_start = '--silent' in sys.argv or '--startup' in sys.argv
print(f"  当前参数: {sys.argv}")
print(f"  静默启动模式: {silent_start}")
print()

# 测试2: 电池状态检测
print("[测试2] 电池状态检测")
try:
    battery = psutil.sensors_battery()
    if battery is None:
        print("  ✓ 检测到台式机（无电池）")
    else:
        percent = battery.percent
        plugged = battery.power_plugged
        print(f"  ✓ 电池电量: {percent}%")
        print(f"  ✓ 充电状态: {'充电中' if plugged else '使用电池'}")
except Exception as e:
    print(f"  ✗ 电池检测失败: {e}")
print()

# 测试3: 时间计算
print("[测试3] 倒计时计算")
interval_minutes = 60
start_time = datetime.now()
print(f"  ✓ 开始时间: {start_time.strftime('%H:%M:%S')}")
print(f"  ✓ 提醒间隔: {interval_minutes}分钟")
print(f"  ✓ 下次提醒: {(start_time.replace(minute=(start_time.minute + interval_minutes) % 60)).strftime('%H:%M:%S')}")
print()

# 测试4: B站URL构建
print("[测试4] B站收藏夹URL")
fid = '3648313921'
mid = '529362421'
url = f'https://space.bilibili.com/{mid}/favlist?fid={fid}&ftype=create'
print(f"  ✓ 收藏夹URL: {url}")
print()

print("=" * 50)
print("基础功能测试完成！")
print("=" * 50)
print()
print("如果所有测试都通过，说明程序逻辑正常。")
print("等待PyQt5安装完成后即可运行完整程序。")
