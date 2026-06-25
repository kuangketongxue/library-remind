@echo off
chcp 65001 >nul
echo ====================================
echo   Rest Reminder - Start Script
echo ====================================
echo.

set "PYTHON=C:\Python314\python.exe"
set "APP_DIR=%~dp0"

if not exist "%PYTHON%" (
    echo [ERROR] python.exe not found
    pause
    exit /b 1
)

echo [INFO] Python: %PYTHON%
echo [INFO] Script: %APP_DIR%rest_reminder.py
echo.

start "" /b "%PYTHON%" "%APP_DIR%rest_reminder.py" --silent

echo [DONE] Launched. Check system tray.
echo.
timeout /t 3 >nul
