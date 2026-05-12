@echo off
title 休息提醒 - 卸载
chcp 65001 >nul

set CURRENT_DIR=%~dp0

REM Remove autostart shortcut
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk"
    echo 已移除开机自启动快捷方式
) else (
    echo 未找到自启动快捷方式
)

REM Stop watchdog if running
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "watchdog.py" >NUL
if not errorlevel 1 (
    taskkill /FI "IMAGENAME eq pythonw.exe" /IMAGENAME "watchdog.py" /F 2>nul
    echo 已关闭看门狗进程
) else (
    echo 未检测到正在运行的看门狗
)

echo.
echo 卸载完成！
echo.