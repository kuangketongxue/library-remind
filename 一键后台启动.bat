@echo off
chcp 65001 >nul

REM 直接使用 wscript 启动 VBS，完全后台运行
wscript.exe "完全独立启动.vbs"

REM 不显示任何消息，直接退出
exit
