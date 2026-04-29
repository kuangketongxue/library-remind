@echo off
chcp 65001 >nul
echo ====================================
echo    休息提醒挂件 - 启动脚本
echo ====================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [信息] 正在后台启动休息提醒挂件...
echo.

REM 使用pythonw启动程序（无控制台窗口，独立进程）
start "" /B pythonw rest_reminder.py

if errorlevel 1 (
    echo [错误] 程序启动失败
    echo 请检查是否已安装依赖: pip install -r requirements.txt
    pause
    exit /b 1
)

echo [成功] 程序已在后台启动
echo 挂件将显示在屏幕右侧
echo 可通过系统托盘图标控制显示/隐藏
echo.
echo 注意：关闭此窗口不会影响程序运行
echo.
timeout /t 3 >nul
