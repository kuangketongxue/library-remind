@echo off
chcp 65001 >nul
title 诊断休息提醒程序
color 0B

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          诊断休息提醒程序启动状态                          ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [步骤 1] 检查Python进程...
echo.
tasklist | findstr /i "python"
if %errorlevel% equ 0 (
    echo.
    echo ✓ 发现Python进程正在运行
) else (
    echo.
    echo ✗ 没有Python进程在运行
    echo.
    echo 正在启动程序...
    start "" pythonw rest_reminder.py
    timeout /t 3 /nobreak >nul
)

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 2] 检查锁文件...
echo.
if exist "%TEMP%\rest_reminder.lock" (
    echo ✓ 锁文件存在: %TEMP%\rest_reminder.lock
    echo.
    echo 锁文件内容（PID）:
    type "%TEMP%\rest_reminder.lock"
    echo.
) else (
    echo ✗ 锁文件不存在
)

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 3] 检查依赖包...
echo.
python -c "import PyQt5; print('✓ PyQt5 已安装')" 2>nul || echo ✗ PyQt5 未安装
python -c "import psutil; print('✓ psutil 已安装')" 2>nul || echo ✗ psutil 未安装
python -c "import requests; print('✓ requests 已安装')" 2>nul || echo ✗ requests 未安装

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 4] 测试程序启动...
echo.
echo 正在测试启动（5秒后自动结束）...
echo.

REM 启动程序并等待5秒
start "" python rest_reminder.py
timeout /t 5 /nobreak >nul

echo.
echo 如果看到窗口，说明程序正常。
echo 如果没有看到窗口，可能是以下原因：
echo   1. 窗口在其他窗口后面
echo   2. 窗口位置超出屏幕范围
echo   3. PyQt5 显示问题
echo.

echo ════════════════════════════════════════════════════════════
echo 诊断完成
echo ════════════════════════════════════════════════════════════
echo.
echo 请检查：
echo   1. 系统托盘（任务栏右下角）是否有程序图标
echo   2. 屏幕右侧中间是否有半透明窗口
echo   3. 按 Alt+Tab 查看是否有"休息提醒"窗口
echo.
echo 如果仍然看不到，请按任意键清理进程...
pause >nul

echo.
echo 正在清理测试进程...
taskkill /F /IM python.exe /T 2>nul
taskkill /F /IM pythonw.exe /T 2>nul

echo.
echo 清理完成！
echo.
pause
