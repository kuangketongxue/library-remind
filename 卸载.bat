@echo off
title 休息提醒 - 卸载
chcp 65001 >nul

set CURRENT_DIR=%~dp0

REM Remove autostart: 注册表 Run 键 + StartupApproved + .lnk 冗余快捷方式（三处都清理，避免双启动残留）
set REG_RUN="HKCU\Software\Microsoft\Windows\CurrentVersion\Run"
reg delete %REG_RUN% /v "RestReminder" /f >nul 2>&1
if errorlevel 1 (
    echo 注册表 Run 键未找到（已被清理）
) else (
    echo 已移除注册表 Run 键自启动
)
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\StartupApproved\Run" /v "RestReminder" /f >nul 2>&1
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk"
    echo 已移除启动文件夹快捷方式
) else (
    echo 未找到启动文件夹快捷方式
)

REM Stop program if running
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "rest_reminder.py" >NUL
if not errorlevel 1 (
    taskkill /FI "IMAGENAME eq pythonw.exe" /IMAGENAME "rest_reminder.py" /F 2>nul
    echo 已关闭程序进程
) else (
    echo 未检测到正在运行的程序
)

echo.
echo 卸载完成！
echo.