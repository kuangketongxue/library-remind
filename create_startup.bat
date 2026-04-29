@echo off
chcp 65001 >nul
echo ====================================
echo    休息提醒 - 设置开机自启动
echo ====================================
echo.

REM 获取当前目录
set CURRENT_DIR=%~dp0
set SCRIPT_PATH=%CURRENT_DIR%rest_reminder.py

REM 获取Python路径
for /f "tokens=*" %%i in ('where pythonw') do set PYTHONW_PATH=%%i

if "%PYTHONW_PATH%"=="" (
    echo [错误] 未找到 pythonw.exe
    echo 请确保Python已正确安装
    pause
    exit /b 1
)

REM 获取启动文件夹路径
set STARTUP_FOLDER=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup

REM 创建VBS脚本来创建快捷方式
set VBS_FILE=%TEMP%\create_shortcut.vbs
echo Set oWS = WScript.CreateObject("WScript.Shell") > %VBS_FILE%
echo sLinkFile = "%STARTUP_FOLDER%\休息提醒.lnk" >> %VBS_FILE%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %VBS_FILE%
echo oLink.TargetPath = "%PYTHONW_PATH%" >> %VBS_FILE%
echo oLink.Arguments = """%SCRIPT_PATH%""" --startup" >> %VBS_FILE%
echo oLink.WorkingDirectory = "%CURRENT_DIR%" >> %VBS_FILE%
echo oLink.Description = "每小时休息提醒挂件" >> %VBS_FILE%
echo oLink.WindowStyle = 7 >> %VBS_FILE%
echo oLink.Save >> %VBS_FILE%

REM 执行VBS脚本
cscript //nologo %VBS_FILE%

REM 删除临时VBS文件
del %VBS_FILE%

echo.
echo ✓ 开机自启动设置成功！
echo.
echo 快捷方式位置: %STARTUP_FOLDER%\休息提醒.lnk
echo 目标程序: %PYTHONW_PATH%
echo 脚本路径: %SCRIPT_PATH%
echo.
echo ✓ 程序将在开机时自动后台启动（静默模式）
echo ✓ 不会显示任何窗口或提示
echo ✓ 只在系统托盘显示图标
echo.
pause
