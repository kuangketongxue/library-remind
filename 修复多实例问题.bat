@echo off
chcp 65001 >nul
title 修复多实例运行问题
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════╗
echo ║                                                            ║
echo ║          休息提醒程序 - 修复多实例运行问题                ║
echo ║                                                            ║
echo ╚════════════════════════════════════════════════════════════╝
echo.

echo [步骤 1/4] 检查当前运行的进程...
echo.
echo Python进程列表：
tasklist | findstr /i "pythonw.exe python.exe" | findstr /v "findstr"

if %errorlevel% equ 0 (
    echo.
    echo ✓ 发现运行中的Python进程
) else (
    echo.
    echo ℹ 没有发现运行中的Python进程
)

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 2/4] 结束所有Python后台进程
echo ════════════════════════════════════════════════════════════
echo.
echo 即将结束所有 pythonw.exe 和 python.exe 进程...
echo （这将关闭所有后台运行的Python程序）
echo.
pause

taskkill /F /IM pythonw.exe /T >nul 2>&1
taskkill /F /IM python.exe /T >nul 2>&1

echo.
echo ✓ 已结束所有Python进程

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 3/4] 清理锁文件
echo ════════════════════════════════════════════════════════════
echo.

if exist "%TEMP%\rest_reminder.lock" (
    del "%TEMP%\rest_reminder.lock"
    echo ✓ 已删除锁文件: %TEMP%\rest_reminder.lock
) else (
    echo ℹ 锁文件不存在，无需清理
)

echo.
echo ════════════════════════════════════════════════════════════
echo [步骤 4/4] 重新启动程序
echo ════════════════════════════════════════════════════════════
echo.
echo 是否立即启动休息提醒程序？
echo.
echo [1] 是 - 启动程序（后台运行）
echo [2] 否 - 稍后手动启动
echo.
choice /c 12 /n /m "请选择 (1 或 2): "

if errorlevel 2 goto :skip_start
if errorlevel 1 goto :do_start

:do_start
echo.
echo 正在启动程序...

REM 查找Python路径
set PYTHON_PATH=
for /f "delims=" %%i in ('where pythonw 2^>nul') do set PYTHON_PATH=%%i

if not defined PYTHON_PATH (
    echo ❌ 未找到 pythonw.exe，请确保Python已正确安装
    goto :end
)

REM 获取当前目录
set CURRENT_DIR=%~dp0
set SCRIPT_PATH=%CURRENT_DIR%rest_reminder.py

REM 启动程序
start "" "%PYTHON_PATH%" "%SCRIPT_PATH%" --startup

timeout /t 2 /nobreak >nul

echo.
echo ✓ 程序已启动！
echo.
echo 请检查系统托盘（任务栏右下角）是否有程序图标。
echo 双击托盘图标可显示窗口。

goto :end

:skip_start
echo.
echo ℹ 已跳过启动，您可以稍后手动启动程序。

:end
echo.
echo ════════════════════════════════════════════════════════════
echo 修复完成！
echo ════════════════════════════════════════════════════════════
echo.
echo 说明：
echo - 程序现在具有单实例保护，不会重复启动
echo - 如果再次遇到多实例问题，请重新运行此脚本
echo - 更多信息请查看：单实例功能说明.md
echo.
pause
