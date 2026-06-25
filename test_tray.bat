@echo off
chcp 65001 >nul
echo Running tray icon test...
"C:\Python314\python.exe" "%~dp0test_tray.py" 2>&1
echo.
echo If you see a lightning bolt icon in system tray for 5 seconds, it worked.
pause
