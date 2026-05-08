@echo off
chcp 65001 >nul
echo ========================================
echo 清理多余的休息提醒进程
echo ========================================
echo.

echo 正在查找运行中的Python进程...
echo.

REM 显示当前运行的Python进程
echo Python进程列表：
tasklist | findstr /i "python.exe pythonw.exe"

echo.
echo ========================================
echo 即将结束所有Python进程
echo （这将关闭所有后台运行的Python程序）
echo ========================================
echo.
pause

REM 结束所有python.exe进程
taskkill /F /IM python.exe /T 2>nul
set error1=%errorlevel%

REM 结束所有pythonw.exe进程
taskkill /F /IM pythonw.exe /T 2>nul
set error2=%errorlevel%

echo.
if %error1% equ 0 (
    echo ✓ 已成功结束所有python.exe进程
) else (
    echo ℹ 没有找到运行中的python.exe进程
)

if %error2% equ 0 (
    echo ✓ 已成功结束所有pythonw.exe进程
) else (
    echo ℹ 没有找到运行中的pythonw.exe进程
)

echo.
echo 正在清理锁文件...

REM 删除锁文件
del "%TEMP%\rest_reminder.lock" 2>nul

if %errorlevel% equ 0 (
    echo ✓ 已清理锁文件
) else (
    echo ℹ 没有找到锁文件
)

echo.
echo ========================================
echo 清理完成！
echo ========================================
echo.
echo 现在可以重新启动休息提醒程序了。
echo.
pause
