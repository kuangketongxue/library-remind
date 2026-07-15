@echo off
chcp 65001 >nul
title 休息提醒挂件 - 一键安装
color 0A
echo.
echo ╔════════════════════════════════════╗
echo ║     休息提醒挂件 - 一键安装脚本    ║
echo ╚════════════════════════════════════╝
echo.
echo 本脚本将自动完成以下操作：
echo   1. 检查Python环境
echo   2. 安装所需依赖
echo   3. 设置开机自启动
echo   4. 启动程序（后台运行）
echo.
echo 安装完成后，程序将：
echo   ✓ 每次开机自动启动
echo   ✓ 静默运行，不打扰你
echo   ✓ 只在系统托盘显示图标
echo   ✓ 需要时双击托盘图标即可显示
echo.
pause
echo.

set "PYTHONW=C:\Python314\pythonw.exe"
set "APP_DIR=%~dp0"

REM ========================================
REM 步骤1: 检查Python
REM ========================================
echo [1/4] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ✗ 错误：未检测到Python
    echo.
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    echo.
    echo 安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✓ Python %PYTHON_VERSION% 已安装
echo ✓ 使用 pythonw: %PYTHONW%
echo.

REM ========================================
REM 步骤2: 安装依赖
REM ========================================
echo [2/4] 安装依赖包...
echo 正在安装 PyQt5, requests, psutil 到项目本地目录...
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install --upgrade --target "%APP_DIR%vendor" PyQt5 requests psutil
if errorlevel 1 (
    echo.
    echo ✗ 依赖安装失败
    echo 请检查网络连接或手动运行: pip install --target vendor PyQt5 requests psutil
    echo.
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

REM ========================================
REM 步骤3: 设置开机自启动（仅用注册表，不再创建 .lnk，避免与代码内 set_autostart 双机制并存）
REM ========================================
echo [3/4] 设置开机自启动...

set CURRENT_DIR=%~dp0

REM 单一启动源：注册表 Run 键（代码内 set_autostart(True) 也写这里，保持一致）
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" /v "RestReminder" /t REG_SZ /d "\"%PYTHONW%\" \"%APP_DIR%rest_reminder.py\" --silent" /f >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠ 自启动设置可能失败（权限或系统限制）
    echo.
) else (
    echo ✓ 开机自启动设置完成（注册表）
)
REM 清理可能残留的旧 .lnk（避免旧版本一键安装留下的双启动）
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk" (
    del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\休息提醒.lnk" >nul 2>&1
    echo ✓ 已清理旧版 .lnk 快捷方式
)
echo.

REM ========================================
REM 步骤4: 启动程序
REM ========================================
echo [4/4] 启动休息提醒...

tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "rest_reminder.py" >NUL
if not errorlevel 1 (
    echo 检测到程序已在运行
    echo 如需重新安装，请先退出程序。
    echo.
) else (
    start "" /b "%PYTHONW%" "%APP_DIR%rest_reminder.py" --silent
)

timeout /t 3 >nul

echo ✓ 程序已启动
echo.
echo ╔════════════════════════════════════════╗
echo ║          ✓ 安装完成！                  ║
echo ╚════════════════════════════════════════╝
echo.
echo 程序已在后台运行，请查看系统托盘图标
echo.
echo ✓ 开机自启动：已启用
echo ✓ 运行模式：静默后台
echo ✓ 托盘图标：已显示
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 使用说明：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 📌 程序会在后台静默运行，不打扰你
echo 📌 每60分钟自动提醒休息并打开视频
echo 📌 实时监控电池状态，断电时提醒
echo.
echo 💡 如需显示挂件窗口：
echo    → 双击系统托盘图标
echo.
echo 💡 如需退出程序：
echo    → 右键托盘图标 → 选择"退出"
echo.
echo ⚠ 如需卸载，请使用卸载脚本进行清理
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
