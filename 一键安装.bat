@echo off
chcp 65001 >nul
title 休息提醒挂件 - 一键安装
color 0A

echo.
echo ╔════════════════════════════════════════╗
echo ║     休息提醒挂件 - 一键安装脚本        ║
echo ╚════════════════════════════════════════╝
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
echo.

REM ========================================
REM 步骤2: 安装依赖
REM ========================================
echo [2/4] 安装依赖包...
echo 正在安装 PyQt5, requests, psutil...
echo.
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ✗ 依赖安装失败
    echo 请检查网络连接或手动运行: pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

REM ========================================
REM 步骤3: 设置开机自启动
REM ========================================
echo [3/4] 设置开机自启动...

REM 获取当前目录和Python路径
set CURRENT_DIR=%~dp0
set SCRIPT_PATH=%CURRENT_DIR%rest_reminder.py

for /f "tokens=*" %%i in ('where pythonw') do set PYTHONW_PATH=%%i

if "%PYTHONW_PATH%"=="" (
    echo ✗ 未找到 pythonw.exe
    pause
    exit /b 1
)

REM 获取启动文件夹路径
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM 使用PowerShell创建快捷方式（更可靠，避免VBS语法错误）
powershell -ExecutionPolicy Bypass -Command "& { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\休息提醒.lnk'); $Shortcut.TargetPath = '%PYTHONW_PATH%'; $Shortcut.Arguments = '\"%SCRIPT_PATH%\" --startup'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = '每小时休息提醒挂件（自动启动）'; $Shortcut.WindowStyle = 7; $Shortcut.Save() }"

echo ✓ 开机自启动设置完成
echo.

REM ========================================
REM 步骤4: 启动程序
REM ========================================
echo [4/4] 启动程序...

REM 检查程序是否已在运行
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "pythonw.exe" >NUL
if not errorlevel 1 (
    echo 检测到程序可能已在运行
    echo 如需重启，请先在托盘图标右键选择"退出"
    echo.
)

REM 静默启动程序
start "" pythonw "%SCRIPT_PATH%" --startup

REM 等待程序启动
timeout /t 2 >nul

echo ✓ 程序已启动
echo.

REM ========================================
REM 安装完成
REM ========================================
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
echo 💡 下次开机会自动启动，无需任何操作
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause
