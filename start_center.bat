@echo off
chcp 65001 >nul
echo 启动休息提醒（窗口居中显示）...
python -c "import sys; sys.argv.append('--center'); exec(open('rest_reminder.py').read())"
