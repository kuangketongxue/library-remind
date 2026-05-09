@echo off
chcp 65001 >nul
echo ========================================
echo    休息提醒 - 后台启动
echo ========================================
echo.
echo [启动中] 正在后台启动程序...
echo.

REM 使用 start 命令启动 VBS 脚本，完全独立运行
start "" wscript.exe "start.vbs"

echo ✓ 程序已在后台启动！
echo.
echo [提示] 程序已经在后台运行
echo        - 不会显示任何窗口
echo        - 只在系统托盘显示图标
echo        - 关闭此窗口不影响程序运行
echo        - 双击托盘图标可显示主窗口
echo.
echo ========================================
echo.

timeout /t 3 >nul
exit
