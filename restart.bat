@echo off
chcp 65001 >nul
echo 停止旧进程...
taskkill /f /fi "WINDOWTITLE eq 休息提醒*" 2>nul
timeout /t 2 /nobreak >nul
echo 启动休息提醒...
start "" /b "C:\Python314\pythonw.exe" "%~dp0rest_reminder.py" --silent
echo 已启动
