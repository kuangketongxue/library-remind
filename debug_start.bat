@echo off
chcp 65001 >nul
set "PYTHON=C:\Python314\python.exe"
set "APP_DIR=%~dp0"
set "ERRLOG=%APP_DIR%launch_error.log"

echo [INFO] Starting...
echo [INFO] Python: %PYTHON%
echo [INFO] Script: %APP_DIR%rest_reminder.py
echo.

REM 直接运行（不 start /b），输出重定向到错误日志
"%PYTHON%" "%APP_DIR%rest_reminder.py" --silent 2>"%ERRLOG%"

echo [EXIT] Process ended, check %ERRLOG% for errors
pause
