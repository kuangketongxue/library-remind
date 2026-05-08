@echo off
chcp 65001 >nul
echo ========================================
echo    测试后台运行功能
echo ========================================
echo.
echo [步骤 1] 启动程序...
call 一键后台启动.bat
timeout /t 2 >nul

echo.
echo [步骤 2] 检查进程...
tasklist | findstr /i "pythonw.exe" >nul
if %errorlevel% == 0 (
    echo ✓ 程序已启动！
    echo.
    echo [进程信息]
    tasklist | findstr /i "pythonw.exe"
) else (
    echo ✗ 未检测到程序进程
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo    测试说明
echo ========================================
echo.
echo 1. 程序已在后台启动
echo 2. 请检查系统托盘（任务栏右下角）
echo 3. 应该能看到程序图标
echo 4. 双击图标可显示主窗口
echo.
echo [测试] 现在关闭此窗口...
echo        程序应该继续在后台运行！
echo.
echo 按任意键关闭此窗口...
pause >nul

echo.
echo [验证] 窗口关闭后，请：
echo        1. 检查托盘图标是否还在
echo        2. 双击托盘图标查看主窗口
echo        3. 如果都正常，说明后台运行成功！
echo.
timeout /t 3 >nul
