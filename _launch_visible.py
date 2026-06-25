import subprocess, time, ctypes

# Launch rest_reminder in non-silent mode (main window visible)
proc = subprocess.Popen(
    [r'C:\Python314\python.exe', r'C:\Users\binlo\Desktop\休息提醒\rest_reminder.py'],
    creationflags=0x00000008  # CREATE_NO_WINDOW
)
print(f'Launched PID: {proc.pid}')

# Wait for window to appear, then bring to front
time.sleep(3)

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def find_window_by_pid(pid):
    result = []
    def callback(hwnd, _):
        _, found_pid = kernel32.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            result.append(hwnd)
        return True
    WNDENUMPROC = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32.EnumWindows(WNDENUMPROC(callback), 0)
    return result

hwnds = find_window_by_pid(proc.pid)
if hwnds:
    hwnd = hwnds[0]
    if user32.IsIconic(hwnd):
        user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    print(f'Brought window to front: {hwnd}')
else:
    print('Window not found yet')
