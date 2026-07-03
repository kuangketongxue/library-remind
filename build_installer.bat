@echo off
chcp 65001 >nul
title 休息提醒 - 构建安装程序
color 0B

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            休息提醒 - 构建安装程序                            ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╗
echo.

setlocal

:: ============================================================================
:: Step 1: Build EXE with PyInstaller
:: ============================================================================
echo [1/3] 使用 PyInstaller 构建 EXE...

:: Use managed Python 3.13 for building (PyInstaller compatible)
set "PYTHON=C:\Users\binlo\.workbuddy\binaries\python\versions\3.13.12\python.exe"
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%.."

if not exist "%PYTHON%" (
    echo ✗ 未找到 Python 3.13: %PYTHON%
    echo   请确认路径正确
    pause
    exit /b 1
)

cd /D "%PROJECT_DIR%"

:: Install PyInstaller if not present
echo   检查 PyInstaller...
"%PYTHON%" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo   安装 PyInstaller...
    "%PYTHON%" -m pip install pyinstaller
)

:: Clean old build
echo   清理旧构建...
if exist dist rmdir /S /Q dist
if exist build rmdir /S /Q build

:: Build
echo   开始构建...
"%PYTHON%" -m PyInstaller RestReminder.spec
if errorlevel 1 (
    echo ✗ PyInstaller 构建失败
    pause
    exit /b 1
)

if not exist "dist\RestReminder.exe" (
    echo ✗ 构建产物未找到: dist\RestReminder.exe
    pause
    exit /b 1
)

echo ✓ EXE 构建完成
echo.

:: ============================================================================
:: Step 2: Prepare installer files
:: ============================================================================
echo [2/3] 准备安装程序文件...

:: Create output directory
if not exist "build\installer" mkdir "build\installer"

:: Copy files needed by installer
echo   复制文件...
copy /Y "dist\RestReminder.exe" "build\installer\" >nul
copy /Y "cute_icon.ico" "build\installer\" >nul
copy /Y "LICENSE" "build\installer\" >nul
copy /Y "README.zh.md" "build\installer\" >nul

echo ✓ 文件准备完成
echo.

:: ============================================================================
:: Step 3: Build Inno Setup installer
:: ============================================================================
echo [3/3] 生成 Inno Setup 安装程序...

:: Check for Inno Setup
where iscc >nul 2>&1
if errorlevel 1 (
    echo ⚠ Inno Setup (iscc) 未找到
    echo.
    echo   请安装 Inno Setup: https://jrsoftware.org/isdl.php
    echo   安装后重新运行此脚本
    echo.
    echo   或手动运行:
    echo   iscc installer\RestReminder.iss
    pause
    exit /b 1
)

:: Compile installer
cd /D "%PROJECT_DIR%\installer"
iscc RestReminder.iss
if errorlevel 1 (
    echo ✗ Inno Setup 编译失败
    pause
    exit /b 1
)

cd /D "%PROJECT_DIR%"

echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║                                                              ║
echo ║            构建完成！                                         ║
echo ║                                                              ║
echo ╚══════════════════════════════════════════════════════════════╗
echo.
echo   安装程序位置: build\installer\RestReminder-Setup-v6.1.7.exe
echo.
echo   运行安装程序进行安装，或直接分发 build\installer\ 目录
echo.

pause

endlocal
