@echo off
chcp 65001 >nul
title 休息提醒 - 快速测试
color 0A

echo.
echo ╔════════════════════════════════════════╗
echo ║     休息提醒 - 快速测试                ║
echo ╚════════════════════════════════════════╝
echo.

echo [1/3] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python未安装
    pause
    exit /b 1
)
for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python %%i
echo.

echo [2/3] 检查依赖包...
python -c "import PyQt5; import requests; import psutil; print('✓ 所有依赖已安装')" 2>nul
if errorlevel 1 (
    echo ✗ 依赖包未安装，请运行 一键安装.bat
    pause
    exit /b 1
)
echo.

echo [3/3] 启动程序（5秒后自动关闭测试窗口）...
echo.
echo 程序将在新窗口中启动...
echo 请检查：
echo   1. 窗口是否正常显示
echo   2. 系统托盘是否有图标
echo   3. 倒计时是否正常运行
echo   4. 电池状态是否显示
echo.

start "" python rest_reminder.py

echo.
echo ✓ 程序已启动！
echo.
echo 如果看到程序窗口和托盘图标，说明修复成功！
echo.
echo 提示：
echo   - 双击托盘图标可显示/隐藏窗口
echo   - 右键托盘图标可退出程序
echo.
pause
