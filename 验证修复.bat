@echo off
chcp 65001 >nul
echo ========================================
echo    休息提醒 - 验证修复结果
echo ========================================
echo.

REM 检查启动文件夹
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

echo [1] 检查启动文件夹...
echo 位置: %STARTUP_FOLDER%
echo.

REM 检查是否存在错误的VBS文件
if exist "%STARTUP_FOLDER%\EyeTimer.vbs" (
    echo × 发现错误文件: EyeTimer.vbs
    echo   建议删除此文件
    echo.
) else (
    echo ✓ 未发现错误的 EyeTimer.vbs 文件
    echo.
)

REM 检查快捷方式
if exist "%STARTUP_FOLDER%\休息提醒.lnk" (
    echo ✓ 找到开机自启动快捷方式
    echo   位置: %STARTUP_FOLDER%\休息提醒.lnk
    echo.
) else (
    echo × 未找到开机自启动快捷方式
    echo   请运行 create_startup.bat 创建
    echo.
)

echo [2] 检查Python环境...
where pythonw >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Python环境正常
    for /f "tokens=*" %%i in ('where pythonw') do echo   路径: %%i
    echo.
) else (
    echo × 未找到 pythonw.exe
    echo   请确保Python已正确安装
    echo.
)

echo [3] 检查程序文件...
if exist "rest_reminder.py" (
    echo ✓ 主程序文件存在
    echo.
) else (
    echo × 未找到 rest_reminder.py
    echo.
)

echo ========================================
echo    验证完成
echo ========================================
echo.
echo 如果所有检查都通过，说明修复成功！
echo.
pause
