@echo off
chcp 65001 >nul
title 休息提醒 - 安装程序
color 0A
setlocal enabledelayedexpansion

:: ============================================================================
:: RestReminder Installer Batch Script
:: 功能：协议确认、安装、创建快捷方式
:: ============================================================================

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            休息提醒 v6.1.7 - 安装程序                         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╗
echo.
echo   本程序将为您安装休息提醒桌面挂件
echo   安装前请仔细阅读以下协议
echo.
echo ════════════════════════════════════════════════════════════════
echo   用户协议
echo ════════════════════════════════════════════════════════════════
echo.
echo   1. 本软件为免费开源软件，仅供个人学习使用
echo   2. 本软件不会收集您的任何个人数据
echo   3. 本软件不会自动上传数据到任何服务器
echo   4. 您可以选择是否开启 AI 学习分析功能（需要配置 API Key）
echo   5. 本软件按"现状"提供，不提供任何明示或暗示的保证
echo   6. 使用本软件产生的任何后果由使用者自行承担
echo.
echo ════════════════════════════════════════════════════════════════
echo   隐私政策
echo ════════════════════════════════════════════════════════════════
echo.
echo   本软件尊重并保护您的隐私：
echo   • 所有学习数据仅存储在本地计算机
echo   • 不会收集任何个人信息
echo   • 不会跟踪您的使用行为
echo   • 飞书日程集成仅在本地运行，不上传数据
echo   • AI 报告功能仅在使用时发送数据到您配置的 API
echo.
echo ════════════════════════════════════════════════════════════════
echo   开源协议
echo ════════════════════════════════════════════════════════════════
echo.
echo   本软件基于 MIT 协议开源
echo   您可以在以下地址查看源代码：
echo   https://github.com/binlo/rest-reminder
echo.
echo ════════════════════════════════════════════════════════════════
echo.

:: ============================================================================
:: Step 1: Protocol Confirmation
:: ============================================================================
set /p agree="是否同意以上协议？(y/n): "
if /i not "%agree%"=="y" (
    echo.
    echo 安装已取消。您必须同意协议才能继续安装。
    pause
    exit /b 1
)

echo.
echo ✓ 已同意用户协议
echo ✓ 已同意隐私政策
echo ✓ 已同意开源协议
echo.

:: ============================================================================
:: Step 2: Choose Installation Directory
:: ============================================================================
set "DEFAULT_DIR=%ProgramFiles%\休息提醒"
set /p INSTALL_DIR="请输入安装目录（默认: %DEFAULT_DIR%）: "
if "!INSTALL_DIR!"=="" set "INSTALL_DIR=%DEFAULT_DIR%"

:: Remove quotes if any
set "INSTALL_DIR=!INSTALL_DIR:"=!"

echo.
echo 安装目录: !INSTALL_DIR!
echo.

:: Create directory
if not exist "!INSTALL_DIR!" (
    echo 正在创建安装目录...
    mkdir "!INSTALL_DIR!" 2>nul
    if errorlevel 1 (
        echo ✗ 创建目录失败，请检查权限或选择其他目录
        pause
        exit /b 1
    )
    echo ✓ 目录创建成功
) else (
    echo ✓ 目录已存在
)

:: ============================================================================
:: Step 3: Copy Files
:: ============================================================================
echo.
echo 正在安装文件...
echo.

:: Copy main executable
echo   复制 RestReminder.exe...
copy /Y "%~dp0dist\RestReminder.exe" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo   ✗ 复制失败
    pause
    exit /b 1
)
echo   ✓ 复制成功

:: Copy icon
echo   复制图标文件...
copy /Y "%~dp0cute_icon.ico" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo   ✗ 复制失败
    pause
    exit /b 1
)
echo   ✓ 复制成功

:: Copy license
echo   复制许可文件...
copy /Y "%~dp0LICENSE" "!INSTALL_DIR!\" >nul
if errorlevel 1 (
    echo   ✗ 复制失败
    pause
    exit /b 1
)
echo   ✓ 复制成功

echo.
echo ✓ 文件安装完成

:: ============================================================================
:: Step 4: Create Shortcuts
:: ============================================================================
echo.
echo 正在创建快捷方式...

:: Get Start Menu path
set "STARTMENU=%ProgramData%\Microsoft\Windows\Start Menu\Programs"
if not exist "%STARTMENU%" set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"

:: Create Start Menu folder
set "STARTMENU_DIR=%STARTMENU%\休息提醒"
if not exist "!STARTMENU_DIR!" mkdir "!STARTMENU_DIR!"

:: Create Start Menu shortcut
echo   创建开始菜单快捷方式...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!STARTMENU_DIR!\休息提醒.lnk'); $Shortcut.TargetPath = '!INSTALL_DIR!\RestReminder.exe'; $Shortcut.WorkingDirectory = '!INSTALL_DIR!'; $Shortcut.IconLocation = '!INSTALL_DIR!\cute_icon.ico,0'; $Shortcut.Description = '休息提醒 - 专注力管理挂件'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo   ✗ 创建开始菜单快捷方式失败
) else (
    echo   ✓ 开始菜单快捷方式已创建
)

:: Create Desktop shortcut
echo   创建桌面快捷方式...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\休息提醒.lnk'); $Shortcut.TargetPath = '!INSTALL_DIR!\RestReminder.exe'; $Shortcut.WorkingDirectory = '!INSTALL_DIR!'; $Shortcut.IconLocation = '!INSTALL_DIR!\cute_icon.ico,0'; $Shortcut.Description = '休息提醒 - 专注力管理挂件'; $Shortcut.Save()" 2>nul
if errorlevel 1 (
    echo   ✗ 创建桌面快捷方式失败（可能需要手动创建）
) else (
    echo   ✓ 桌面快捷方式已创建
)

:: Create Uninstaller shortcut in Start Menu
echo   创建卸载快捷方式...
powershell -Command "$WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('!STARTMENU_DIR!\卸载.lnk'); $Shortcut.TargetPath = '%SystemRoot%\System32\control.exe'; $Shortcut.Arguments = 'appwiz.cpl'; $Shortcut.Description = '卸载休息提醒'; $Shortcut.Save()" 2>nul

echo.
echo ✓ 快捷方式创建完成

:: ============================================================================
:: Step 5: Completion
:: ============================================================================
echo.
echo ════════════════════════════════════════════════════════════════
echo   安装完成！
echo ════════════════════════════════════════════════════════════════
echo.
echo   安装位置: !INSTALL_DIR!
echo   开始菜单: !STARTMENU_DIR!
echo   桌面快捷方式: %USERPROFILE%\Desktop\休息提醒.lnk
echo.

:: Ask to run the application
set /p run_now="是否立即运行休息提醒？(y/n): "
if /i "%run_now%"=="y" (
    echo.
    echo 正在启动休息提醒...
    start "" "!INSTALL_DIR!\RestReminder.exe"
    echo ✓ 已启动
)

:: Ask to view info
set /p view_info="是否查看重要更新信息？(y/n): "
if /i "%view_info%"=="y" (
    echo.
    echo ════════════════════════════════════════════════════════════════
    echo   重要更新信息
    echo ════════════════════════════════════════════════════════════════
    echo.
    echo   v6.1.7 (2026-07-04)
    echo   • 修复了设置保存时的崩溃问题 (import copy 缺失)
    echo   • 修复了复盘弹窗崩溃问题 (QSlider GC)
    echo   • 优化了 AI 服务信息展示
    echo   • 更新了文档与当前实现同步
    echo.
    echo   详细更新日志：
    echo   https://github.com/binlo/rest-reminder/blob/main/CHANGELOG.md
    echo.
)

echo.
echo ════════════════════════════════════════════════════════════════
echo   感谢安装休息提醒！
echo   如有问题请访问：https://github.com/binlo/rest-reminder
echo ════════════════════════════════════════════════════════════════
echo.
pause

endlocal
