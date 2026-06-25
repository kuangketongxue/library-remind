@echo off
chcp 65001 >nul
cd /d "C:\Users\binlo\Desktop\休息提醒"
C:\Python314\python.exe test_tray.py > tray_output.txt 2>&1
