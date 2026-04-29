"""
设置开机自启动脚本
Windows系统通过添加到启动文件夹实现
"""
import os
import sys
import winshell
from win32com.client import Dispatch


def create_startup_shortcut():
    """创建开机自启动快捷方式"""
    # 获取启动文件夹路径
    startup_folder = winshell.startup()
    
    # 获取当前脚本的完整路径
    script_path = os.path.abspath('rest_reminder.py')
    python_path = sys.executable
    
    # 快捷方式路径
    shortcut_path = os.path.join(startup_folder, '休息提醒.lnk')
    
    # 创建快捷方式
    shell = Dispatch('WScript.Shell')
    shortcut = shell.CreateShortCut(shortcut_path)
    shortcut.TargetPath = python_path
    shortcut.Arguments = f'"{script_path}"'
    shortcut.WorkingDirectory = os.path.dirname(script_path)
    shortcut.IconLocation = python_path
    shortcut.Description = '每小时休息提醒挂件'
    shortcut.save()
    
    print(f'✓ 已创建开机自启动快捷方式: {shortcut_path}')
    print(f'  目标程序: {python_path}')
    print(f'  脚本路径: {script_path}')
    return True


def remove_startup_shortcut():
    """移除开机自启动快捷方式"""
    startup_folder = winshell.startup()
    shortcut_path = os.path.join(startup_folder, '休息提醒.lnk')
    
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)
        print(f'✓ 已移除开机自启动快捷方式: {shortcut_path}')
        return True
    else:
        print('× 未找到开机自启动快捷方式')
        return False


if __name__ == '__main__':
    print('=' * 50)
    print('休息提醒 - 开机自启动设置')
    print('=' * 50)
    print()
    print('1. 添加开机自启动')
    print('2. 移除开机自启动')
    print()
    
    choice = input('请选择操作 (1/2): ').strip()
    
    if choice == '1':
        try:
            create_startup_shortcut()
            print('\n✓ 设置成功！程序将在下次开机时自动启动。')
        except Exception as e:
            print(f'\n× 设置失败: {e}')
    elif choice == '2':
        try:
            remove_startup_shortcut()
            print('\n✓ 移除成功！')
        except Exception as e:
            print(f'\n× 移除失败: {e}')
    else:
        print('\n× 无效的选择')
