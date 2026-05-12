@echo off
title 休息提醒 - 测试看门狗
chcp 65001 >nul

echo.
echo ╔════════════════════════════════════╗
echo ║  看门狗功能测试                      ║
echo ╚════════════════════════════════════╝
echo.

REM Check if watchdog is running
echo [检查] 查找看门狗进程...
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "watchdog.py" >NUL
if not errorlevel 1 (
    echo ✓ 看门狗正在运行
) else (
    echo ! 看门狗未运行，启动...
    start "" /b pythonw "%~dp0watchdog.py"
    timeout /t 3 >nul
)

echo.
echo [检查] 主程序是否响应...
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "rest_reminder.py" >NUL
if not errorlevel 1 (
    echo ✓ 主程序正在运行
) else (
    echo ✗ 主程序未运行
)

echo.
echo [测试] 模拟主程序崩溃...
taskkill /FI "IMAGENAME eq pythonw.exe" /IM "rest_reminder.py" /F 2>nul
timeout /t 2 >nul

echo [等待] 看门狗应自动重启主程序...
timeout /t 6 >nul

REM Check again
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "rest_reminder.py" >NUL
if not errorlevel 1 (
    echo ✓ 看门狗已自动重启主程序
) else (
    echo ✗ 看门狗未重启主程序
)

echo.
echo [清理] 关闭所有相关进程...
taskkill /FI "IMAGENAME eq pythonw.exe" /F 2>nul
timeout /t 1 >nul
echo 完成。
