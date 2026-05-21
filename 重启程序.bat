@echo off
echo ========================================
echo  重启休息提醒程序
echo ========================================
echo.

echo [1/3] 正在停止旧进程...
powershell -Command "Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak > nul

echo [2/3] 正在启动看门狗...
cd /d "%~dp0"
start "" pythonw watchdog.py

echo [3/3] 完成！
echo.
echo ========================================
echo 程序已启动！
echo 查看 crash.log 获取调试信息
echo ========================================
echo.
pause