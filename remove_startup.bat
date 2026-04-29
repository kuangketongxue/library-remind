@echo off
chcp 65001 >nul
echo ====================================
echo    休息提醒 - 移除开机自启动
echo ====================================
echo.

REM 获取启动文件夹路径
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
set SHORTCUT_FILE=%STARTUP_FOLDER%\休息提醒.lnk

if exist "%SHORTCUT_FILE%" (
    del "%SHORTCUT_FILE%"
    echo ✓ 已成功移除开机自启动
    echo.
    echo 删除的快捷方式: %SHORTCUT_FILE%
) else (
    echo × 未找到开机自启动快捷方式
    echo.
    echo 查找位置: %SHORTCUT_FILE%
)

echo.
pause
