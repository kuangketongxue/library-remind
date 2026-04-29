@echo off
chcp 65001 >nul
echo ====================================
echo    休息提醒 - 安装测试
echo ====================================
echo.

echo 正在检查安装状态...
echo.

REM 检查Python
echo [1/4] 检查Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python未安装
    echo.
    goto :end
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python %%i
)

REM 检查依赖
echo [2/4] 检查依赖包...
python -c "import PyQt5" >nul 2>&1
if errorlevel 1 (
    echo ✗ PyQt5未安装
) else (
    echo ✓ PyQt5已安装
)

python -c "import requests" >nul 2>&1
if errorlevel 1 (
    echo ✗ requests未安装
) else (
    echo ✓ requests已安装
)

python -c "import psutil" >nul 2>&1
if errorlevel 1 (
    echo ✗ psutil未安装
) else (
    echo ✓ psutil已安装
)

REM 检查主程序
echo [3/4] 检查主程序...
if exist "rest_reminder.py" (
    echo ✓ rest_reminder.py存在
) else (
    echo ✗ rest_reminder.py不存在
)

REM 检查自启动
echo [4/4] 检查开机自启动...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
if exist "%STARTUP_FOLDER%\休息提醒.lnk" (
    echo ✓ 开机自启动已设置
) else (
    echo ✗ 开机自启动未设置
)

echo.
echo ====================================
echo 测试完成
echo ====================================

:end
echo.
pause
