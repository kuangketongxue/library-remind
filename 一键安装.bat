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
python -m pip install -r %~dp0requirements.txt
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

set CURRENT_DIR=%~dp0

REM 使用PowerShell创建快捷方式到Startup文件夹（更可靠）
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
powershell -ExecutionPolicy Bypass -Command "^&
    `$WshShell = New-Object -ComObject WScript.Shell;^n
    `$Shortcut = `$WshShell.CreateShortcut('%STARTUP_FOLDER%\\休息提醒.lnk');^n
    `$Shortcut.TargetPath = '"%~dp0watchdog.py"';^n
    `$Shortcut.Arguments = '';^n
    `$Shortcut.WorkingDirectory = '%CURRENT_DIR%';^n
    `$Shortcut.Description = '每小时休息提醒挂件（自动启动）';^n
    `$Shortcut.WindowStyle = 7;^n
    `$Shortcut.Save()^n"
if errorlevel 1 (
    echo.
    echo ⚠ 自启动设置可能失败（权限或系统限制）
    echo.
) else (
    echo ✓ 开机自启动设置完成
)
echo.

REM ========================================
REM 步骤4: 启动监视器
REM ========================================
echo [4/4] 启动看门狗监视器...

REM 检查是否已有看门狗在运行
tasklist /FI "IMAGENAME eq pythonw.exe" 2>NUL | find /I "watchdog.py" >NUL
if not errorlevel 1 (
    echo 检测到看门狗已在运行
    echo 如需重新安装，请先退出看门狗。
    echo.
) else (
    REM 静默启动看门狗
    start "" /b pythonw "%CURRENT_DIR%watchdog.py"
)

REM 等待看门狗初始化
timeout /t 3 >nul

echo ✓ 看门狗已启动
echo.

echo ╔════════════════════════════════════════╗
echo ║          ✓ 安装完成！                  ║
echo ╚════════════════════════════════════════╝
echo.
echo 程序已在后台运行，请查看系统托盘图标
echo.
echo ✓ 开机自启动：已启用
echo ✓ 运行模式：静默后台（看门狗守护）
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
echo ⚠ 程序由看门狗守护，请通过托盘图标退出
echo   或使用卸载脚本进行清理
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
pause