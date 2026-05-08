@echo off
chcp 65001 >nul
title 休息提醒 - 完整修复验证
color 0B

echo.
echo ╔════════════════════════════════════════╗
echo ║     休息提醒 - 完整修复验证            ║
echo ╚════════════════════════════════════════╝
echo.

REM ========================================
REM 1. 检查Python环境
REM ========================================
echo [1/6] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python未安装
    goto :error
) else (
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do echo ✓ Python %%i
)
echo.

REM ========================================
REM 2. 检查依赖包
REM ========================================
echo [2/6] 检查依赖包...
python -c "import PyQt5; import requests; import psutil" 2>nul
if errorlevel 1 (
    echo ✗ 依赖包未完整安装
    echo 正在安装依赖...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo ✗ 依赖安装失败
        goto :error
    )
)
echo ✓ PyQt5, requests, psutil 已安装
echo.

REM ========================================
REM 3. 检查主程序文件
REM ========================================
echo [3/6] 检查主程序文件...
if not exist "rest_reminder.py" (
    echo ✗ 主程序文件不存在
    goto :error
)
echo ✓ rest_reminder.py 存在
echo.

REM ========================================
REM 4. 清理启动文件夹中的错误文件
REM ========================================
echo [4/6] 清理启动文件夹...
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM 删除可能存在的错误VBS文件
if exist "%STARTUP_FOLDER%\EyeTimer.vbs" (
    del "%STARTUP_FOLDER%\EyeTimer.vbs"
    echo ✓ 已删除错误的 EyeTimer.vbs
) else (
    echo ✓ 无错误VBS文件
)

REM 删除旧的快捷方式
if exist "%STARTUP_FOLDER%\休息提醒.lnk" (
    del "%STARTUP_FOLDER%\休息提醒.lnk"
    echo ✓ 已删除旧快捷方式
)
echo.

REM ========================================
REM 5. 重新创建正确的快捷方式
REM ========================================
echo [5/6] 创建新的开机自启动快捷方式...

REM 获取Python路径
for /f "tokens=*" %%i in ('where pythonw 2^>nul') do set PYTHONW_PATH=%%i

if "%PYTHONW_PATH%"=="" (
    echo ✗ 未找到 pythonw.exe
    goto :error
)

REM 获取当前目录和脚本路径
set CURRENT_DIR=%~dp0
set SCRIPT_PATH=%CURRENT_DIR%rest_reminder.py

REM 使用PowerShell创建快捷方式
powershell -ExecutionPolicy Bypass -Command "& { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%STARTUP_FOLDER%\休息提醒.lnk'); $Shortcut.TargetPath = '%PYTHONW_PATH%'; $Shortcut.Arguments = '\"%SCRIPT_PATH%\" --startup'; $Shortcut.WorkingDirectory = '%CURRENT_DIR%'; $Shortcut.Description = '每小时休息提醒挂件'; $Shortcut.WindowStyle = 7; $Shortcut.Save(); Write-Host '✓ 快捷方式创建成功' -ForegroundColor Green }"

if errorlevel 1 (
    echo ✗ 快捷方式创建失败
    goto :error
)
echo.

REM ========================================
REM 6. 验证快捷方式
REM ========================================
echo [6/6] 验证快捷方式配置...
powershell -ExecutionPolicy Bypass -Command "& { $shortcut = '%STARTUP_FOLDER%\休息提醒.lnk'; if (Test-Path $shortcut) { $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut($shortcut); Write-Host '✓ 快捷方式存在' -ForegroundColor Green; Write-Host '  目标: ' -NoNewline; Write-Host $Shortcut.TargetPath -ForegroundColor Cyan; Write-Host '  参数: ' -NoNewline; Write-Host $Shortcut.Arguments -ForegroundColor Cyan; Write-Host '  工作目录: ' -NoNewline; Write-Host $Shortcut.WorkingDirectory -ForegroundColor Cyan; Write-Host '  窗口样式: ' -NoNewline; Write-Host $Shortcut.WindowStyle -ForegroundColor Cyan } else { Write-Host '✗ 快捷方式不存在' -ForegroundColor Red; exit 1 } }"

if errorlevel 1 (
    echo ✗ 快捷方式验证失败
    goto :error
)
echo.

REM ========================================
REM 修复完成
REM ========================================
echo.
echo ╔════════════════════════════════════════╗
echo ║          ✓ 修复完成！                  ║
echo ╚════════════════════════════════════════╝
echo.
echo ✓ Python环境正常
echo ✓ 依赖包已安装
echo ✓ 主程序文件存在
echo ✓ 错误文件已清理
echo ✓ 快捷方式已重建
echo ✓ 配置验证通过
echo.
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo 下一步操作：
echo ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
echo.
echo 1. 测试程序启动：
echo    双击 "run.bat" 或 "start.vbs"
echo.
echo 2. 测试开机自启动：
echo    重启电脑，程序会自动后台运行
echo.
echo 3. 查看托盘图标：
echo    程序运行后会在系统托盘显示图标
echo.
echo 4. 显示/隐藏窗口：
echo    双击托盘图标
echo.
echo 5. 退出程序：
echo    右键托盘图标 → 选择"退出"
echo.
goto :end

:error
echo.
echo ╔════════════════════════════════════════╗
echo ║          ✗ 修复失败                    ║
echo ╚════════════════════════════════════════╝
echo.
echo 请检查上述错误信息，或联系技术支持
echo.

:end
echo.
pause
