@echo off
echo ========================================
echo  休息提醒 - 功能测试
echo ========================================
echo.

echo [1/2] 检查进程状态...
tasklist | findstr "pythonw.exe"
echo.

echo [2/2] 检查 crash.log...
if exist crash.log (
    type crash.log
) else (
    echo crash.log 不存在（程序正常运行中）
)

echo.
echo ========================================
echo 测试完成！
pause > nul