@echo off
chcp 65001 >nul
echo ========================================
echo 测试单实例功能
echo ========================================
echo.

echo 第一次启动程序（应该成功）...
start "" pythonw rest_reminder.py --silent
timeout /t 3 /nobreak >nul

echo.
echo 第二次启动程序（应该被阻止）...
python rest_reminder.py

echo.
echo ========================================
echo 测试完成
echo ========================================
echo.
echo 如果看到"程序已在运行中"的提示，说明单实例功能正常。
echo.
echo 请检查系统托盘是否只有一个休息提醒图标。
echo.
pause

echo.
echo 正在清理测试进程...
taskkill /F /IM pythonw.exe /T 2>nul
del "%TEMP%\rest_reminder.lock" 2>nul

echo.
echo 清理完成！
pause
