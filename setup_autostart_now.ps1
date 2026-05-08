# PowerShell脚本 - 立即设置开机自启动

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   休息提醒 - 设置开机自启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 获取路径
$startupFolder = [Environment]::GetFolderPath('Startup')
$pythonw = (Get-Command pythonw).Source
$scriptPath = Join-Path (Get-Location) "rest_reminder.py"
$shortcutPath = Join-Path $startupFolder "休息提醒.lnk"

Write-Host "[信息] 启动文件夹: $startupFolder" -ForegroundColor Yellow
Write-Host "[信息] Python路径: $pythonw" -ForegroundColor Yellow
Write-Host "[信息] 脚本路径: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# 创建快捷方式 - 使用 VBS 脚本启动，确保完全独立运行
$vbsPath = Join-Path (Get-Location) "完全独立启动.vbs"
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$vbsPath`""
$Shortcut.WorkingDirectory = Get-Location
$Shortcut.Description = "每小时休息提醒挂件（自动启动）"
$Shortcut.WindowStyle = 7  # 最小化窗口
$Shortcut.Save()

Write-Host "✓ 开机自启动设置成功！" -ForegroundColor Green
Write-Host ""
Write-Host "快捷方式位置: $shortcutPath" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  设置完成！" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ 程序将在下次开机时自动启动" -ForegroundColor Green
Write-Host "✓ 启动模式：静默后台运行" -ForegroundColor Green
Write-Host "✓ 不会显示任何窗口或提示" -ForegroundColor Green
Write-Host "✓ 只在系统托盘显示图标" -ForegroundColor Green
Write-Host ""
