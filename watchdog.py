"""
休息提醒看门狗 — 监控主进程，崩溃后自动重启
不显示窗口，仅作为后台守护进程运行
"""
import os
import subprocess
import sys
import ctypes
import tempfile
import time

APP_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(APP_DIR, 'rest_reminder.py')
WATCHDOG = os.path.join(APP_DIR, 'watchdog.py')
LOCK_PATH = os.path.join(tempfile.gettempdir(), 'rest_reminder.lock')
PYTHONW = os.path.join(os.path.dirname(sys.executable), 'pythonw.exe')
if not os.path.exists(PYTHONW):
    PYTHONW = sys.executable

# WindowsApps 代理检测：如果 pythonw.exe 是 Store 代理（体积 < 100KB），
# 查找真实 Python 安装目录下的 pythonw.exe
def _find_real_pythonw(candidate):
    """如果 candidate 是 WindowsApps 代理，返回真实 Python 的 pythonw.exe"""
    try:
        if 'WindowsApps' in candidate and os.path.exists(candidate):
            size = os.path.getsize(candidate)
            if size < 100_000:  # 代理文件通常很小
                # 从 PATH 中找非 WindowsApps 的 pythonw
                for p in os.environ.get('PATH', '').split(os.pathsep):
                    if 'WindowsApps' in p:
                        continue
                    real = os.path.join(p, 'pythonw.exe')
                    if os.path.exists(real) and os.path.getsize(real) > 100_000:
                        return real
    except Exception:
        pass
    return candidate

PYTHONW = _find_real_pythonw(PYTHONW)

CRASH_LOG = os.path.join(APP_DIR, 'crash.log')
MAX_RESTARTS = 50
RESTART_DELAY = 3
CRASH_WINDOW = 300  # 5 分钟内反复崩溃则暂停

restart_times = []
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
STILL_ACTIVE = 259


def log_crash(returncode):
    """记录崩溃信息"""
    try:
        with open(CRASH_LOG, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'{datetime.now().isoformat()} 进程退出 code={returncode}\n')
    except Exception:
        pass


def log_event(message):
    try:
        with open(CRASH_LOG, 'a', encoding='utf-8') as f:
            from datetime import datetime
            f.write(f'{datetime.now().isoformat()} {message}\n')
    except Exception:
        pass


def should_pause():
    """检查是否短时间内崩溃过多"""
    now = time.time()
    restart_times[:] = [t for t in restart_times if now - t < CRASH_WINDOW]
    return len(restart_times) >= 5


def _same_script(cmdline, script_path):
    script_path = os.path.normcase(os.path.abspath(script_path))
    for part in cmdline:
        try:
            if os.path.normcase(os.path.abspath(part.strip('"'))) == script_path:
                return True
        except (OSError, ValueError):
            continue
    return False


def is_pid_running(pid):
    try:
        handle = ctypes.windll.kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, int(pid))
        if not handle:
            return False
        code = ctypes.c_ulong()
        ok = ctypes.windll.kernel32.GetExitCodeProcess(handle, ctypes.byref(code))
        ctypes.windll.kernel32.CloseHandle(handle)
        return bool(ok and code.value == STILL_ACTIVE)
    except Exception:
        return False


def lock_pid_running():
    try:
        if not os.path.exists(LOCK_PATH):
            return False
        if time.time() - os.path.getmtime(LOCK_PATH) > 30:
            return False
        with open(LOCK_PATH, 'r', encoding='utf-8') as f:
            pid = f.read().strip()
        return bool(pid and is_pid_running(pid))
    except Exception:
        return False


def acquire_watchdog_mutex():
    name = 'RestReminderWatchdog_' + str(abs(hash(os.path.normcase(WATCHDOG))))
    handle = ctypes.windll.kernel32.CreateMutexW(None, False, name)
    if not handle:
        return None, False
    already_exists = ctypes.windll.kernel32.GetLastError() == 183
    return handle, not already_exists


def main():
    log_event('watchdog started')
    while len(restart_times) < MAX_RESTARTS:
        if lock_pid_running():
            time.sleep(5)
            continue

        if should_pause():
            time.sleep(60)
            continue

        restart_times.append(time.time())
        log_event('starting rest_reminder.py --silent')
        proc = subprocess.Popen(
            [PYTHONW, SCRIPT, '--silent'],
            cwd=APP_DIR,
            creationflags=0x08000000  # CREATE_NO_WINDOW
        )
        started_at = time.time()
        proc.wait()
        runtime = time.time() - started_at
        log_crash(proc.returncode)
        log_event(f'rest_reminder.py exited code={proc.returncode} runtime={runtime:.1f}s')

        if proc.returncode == 0 and runtime > 10:
            log_event(f'进程干净退出 code=0 runtime={runtime:.1f}s，继续守护（不中断）')
            # 不 break：干净退出不代表用户主动关闭，可能是 GC/窗口丢失等意外
            # 只有用户通过托盘菜单"退出"才会真正终止看门狗进程

        time.sleep(RESTART_DELAY)


if __name__ == '__main__':
    mutex_handle, acquired = acquire_watchdog_mutex()
    if not acquired:
        sys.exit(0)

    main()
