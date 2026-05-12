"""
休息提醒看门狗 — 监控主进程，崩溃后自动重启
不显示窗口，仅作为后台守护进程运行
"""
import subprocess
import sys
import os
import time
import psutil

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rest_reminder.py')
PYTHONW = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable

CRASH_LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'crash.log')
MAX_RESTARTS = 50
RESTART_DELAY = 3
CRASH_WINDOW = 300  # 5 分钟内反复崩溃则暂停

restart_times = []


def log_crash(returncode):
    """记录崩溃信息"""
    try:
        with open(CRASH_LOG, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'{datetime.now().isoformat()} 进程退出 code={returncode}\n')
    except Exception:
        pass


def should_pause():
    """检查是否短时间内崩溃过多"""
    now = time.time()
    restart_times[:] = [t for t in restart_times if now - t < CRASH_WINDOW]
    return len(restart_times) >= 5


def main():
    while len(restart_times) < MAX_RESTARTS:
        restart_times.append(time.time())

        if should_pause():
            time.sleep(60)
            continue

        proc = subprocess.Popen(
            [PYTHONW, SCRIPT],
            cwd=os.path.dirname(SCRIPT),
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
        proc.wait()
        log_crash(proc.returncode)

        if proc.returncode == 0:
            break

        time.sleep(RESTART_DELAY)


if __name__ == '__main__':
    # 检查是否已有 watchdog 在运行（检查同目录的脚本）
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'cmdline']):
        try:
            if proc.info['pid'] == current_pid:
                continue
            cmdline = ' '.join(proc.info['cmdline'] or [])
            if 'watchdog.py' in cmdline and 'python' in cmdline.lower():
                sys.exit(0)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    main()
