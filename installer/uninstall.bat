@echo off
chcp 65001 >nul
title 休息提醒 - 卸载程序
color 0C
setlocal enabledelayedexpansion

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            休息提醒 - 卸载程序                                 ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╗
echo.

set "INSTALL_DIR=%ProgramFiles%\休息提醒"
if not exist "%INSTALL_DIR%\RestReminder.exe" (
    echo ✗ 未检测到安装目录: %INSTALL_DIR%
    echo.
    set /p custom_dir="请输入安装目录（或按回车取消）: "
    if "!custom_dir!"=="" (
        echo 卸载已取消。
        pause
        exit /b 1
    )
    set "INSTALL_DIR=!custom_dir:"=!"
)

echo 检测到安装位置: %INSTALL_DIR%
echo.

set /p confirm="确定要卸载休息提醒吗？(y/n): "
if /i not "%confirm%"=="y" (
    echo 卸载已取消。
    pause
    exit /b 1
)

echo.
echo 正在卸载...

:: Remove shortcuts
echo   删除快捷方式...
if exist "%USERPROFILE%\Desktop\休息提醒.lnk" del /F "%USERPROFILE%\Desktop\休息提醒.lnk" 2>nul
if exist "%ProgramData%\Microsoft\Windows\Start Menu\Programs\休息提醒" rmdir /S /Q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\休息提醒" 2>nul
if exist "%APPDATA%\Microsoft\Windows\Start Menu\Programs\休息提醒" rmdir /S /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\休息提醒" 2>nul

:: Kill running process
echo   关闭正在运行的程序...
taskkill /F /IM "RestReminder.exe" >nul 2>&1
timeout /t 1 /nobreak >nul

:: Remove installation directory
echo   删除程序文件...
if exist "%INSTALL_DIR%" rmdir /S /Q "%INSTALL_DIR%"

:: Clean up data (optional)
echo.
set /p cleanup_data="是否删除学习数据（复盘记录、统计数据）？(y/n): "
if /i "!cleanup_data!"=="y" (
    echo   删除数据文件...
    if exist "%LOCALAPPDATA%\RestReminder\.daily_log.json" del /F "%LOCALAPPDATA%\RestReminder\.daily_log.json" 2>nul
    if exist "%LOCALAPPDATA%\RestReminder\.review_log.json" del /F "%LOCALAPPDATA%\RestReminder\.review_log.json" 2>nul
    if exist "%LOCALAPPDATA%\RestReminder\.settings.json" del /F "%LOCALAPPDATA%\RestReminder\.settings.json" 2>nul
    echo   ✓ 数据已删除
) else (
    echo   数据已保留在 %LOCALAPPDATA%\RestReminder\
)

echo.
echo ✓ 卸载完成
echo.
pause

endlocal
