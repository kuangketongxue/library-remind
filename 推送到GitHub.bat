@echo off
chcp 65001 >nul
echo ========================================
echo 休息提醒程序 - 推送到GitHub
echo ========================================
echo.

REM 检查是否安装了 git
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Git!
    echo.
    echo 请先安装 Git:
    echo 1. 访问 https://git-scm.com/download/win
    echo 2. 下载并安装
    echo.
    pause
    exit /b 1
)

echo [1/6] 检查Git状态...
git status
echo.

echo [2/6] 添加所有文件...
git add .
echo.

echo [3/6] 提交更改...
git commit -m "更新：请在此处填写提交说明"
if %errorlevel% neq 0 (
    echo.
    echo [!] 可能没有新的更改需要提交
    echo.
)
echo.

echo [4/6] 检查是否有远程仓库...
git remote -v
echo.

echo.
echo ========================================
echo 如果需要推送到GitHub，请执行：
echo ========================================
echo.
echo git remote add origin ^<你的仓库地址^>
echo git branch -M main
echo git push -u origin main
echo.
echo ========================================
echo.
pause