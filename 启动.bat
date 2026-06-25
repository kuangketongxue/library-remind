@echo off
chcp 65001 >nul
title 休息提醒 - 启动中
echo.
echo 正在启动休息提醒...
echo.

set PYTHONW=C:\Python314\pythonw.exe
set APP_DIR=%~dp0

if not exist "%PYTHONW%" (
    echo [错误] 未找到 pythonw.exe
    pause
    exit /b 1
)

set PYTHONPATH=%APP_DIR%vendor

echo Python: %PYTHONW%
echo 脚本: %APP_DIR%rest_reminder.py
echo.

start "" /b "%PYTHONW%" "%APP_DIR%rest_reminder.py" --silent

echo [完成] 已启动
echo 查看系统托盘是否有图标
echo.
timeout /t 3 >nul
