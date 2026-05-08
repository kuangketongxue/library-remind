@echo off
chcp 65001 >nul
echo ====================================
echo    休息提醒 - 设置开机自启动
echo ====================================
echo.

REM 使用PowerShell来创建快捷方式（更可靠）
powershell -ExecutionPolicy Bypass -Command "& { $startupFolder = [Environment]::GetFolderPath('Startup'); $pythonw = (Get-Command pythonw -ErrorAction SilentlyContinue).Source; if (-not $pythonw) { Write-Host '[错误] 未找到 pythonw.exe' -ForegroundColor Red; Write-Host '请确保Python已正确安装' -ForegroundColor Red; exit 1 }; $currentDir = '%~dp0'; $scriptPath = Join-Path $currentDir 'rest_reminder.py'; $shortcutPath = Join-Path $startupFolder '休息提醒.lnk'; if (Test-Path $shortcutPath) { Remove-Item $shortcutPath -Force; Write-Host '已删除旧的快捷方式' -ForegroundColor Yellow }; $WshShell = New-Object -ComObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut($shortcutPath); $Shortcut.TargetPath = $pythonw; $Shortcut.Arguments = \"`\"$scriptPath`\" --startup\"; $Shortcut.WorkingDirectory = $currentDir; $Shortcut.Description = '每小时休息提醒挂件'; $Shortcut.WindowStyle = 7; $Shortcut.Save(); Write-Host ''; Write-Host '✓ 开机自启动设置成功！' -ForegroundColor Green; Write-Host ''; Write-Host '快捷方式位置: ' -NoNewline; Write-Host $shortcutPath -ForegroundColor Cyan; Write-Host '目标程序: ' -NoNewline; Write-Host $pythonw -ForegroundColor Cyan; Write-Host '脚本路径: ' -NoNewline; Write-Host $scriptPath -ForegroundColor Cyan; Write-Host ''; Write-Host '✓ 程序将在开机时自动后台启动（静默模式）' -ForegroundColor Green; Write-Host '✓ 不会显示任何窗口或提示' -ForegroundColor Green; Write-Host '✓ 只在系统托盘显示图标' -ForegroundColor Green; Write-Host '' }"

echo.
pause
