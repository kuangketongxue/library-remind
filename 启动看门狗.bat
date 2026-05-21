@echo off
echo ========================================
echo 启动休息提醒看门狗
echo ========================================
echo.

cd /d "%~dp0"

echo 正在启动看门狗...
start "" pythonw watchdog.py

echo.
echo 看门狗已启动！
echo 程序将在后台运行
echo 查看 crash.log 文件可以看到测试输出
echo.
pause
