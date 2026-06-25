import psutil, time, os, subprocess, sys

PYTHONW = r'C:\Python314\pythonw.exe'
SCRIPT = os.path.join(os.environ['USERPROFILE'], 'Desktop', '休息提醒', 'rest_reminder.py')
VENDOR = os.path.join(os.environ['USERPROFILE'], 'Desktop', '休息提醒', 'vendor')
LOG = os.path.join(os.environ['USERPROFILE'], 'Desktop', '休息提醒', 'rest_reminder.log')

# Kill old
for p in psutil.process_iter(['pid','name','cmdline']):
    try:
        cmd = ' '.join(p.info['cmdline'] or [])
        if 'rest_reminder' in cmd.lower():
            print(f'Killing {p.pid}...')
            p.kill()
    except:
        pass
time.sleep(2)

# Clear log
with open(LOG, 'w') as f:
    pass

# Launch
env = os.environ.copy()
env['PYTHONPATH'] = VENDOR
proc = subprocess.Popen(
    [PYTHONW, SCRIPT, '--silent'],
    env=env,
    creationflags=0x08000000
)
print(f'Launched PID: {proc.pid}')
print(f'Python: {PYTHONW}')
print(f'Script: {SCRIPT}')
print(f'PYTHONPATH: {VENDOR}')
