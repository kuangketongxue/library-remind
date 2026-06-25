; 截图桌面保存到项目目录
#NoEnv
SetWorkingDir, %A_ScriptDir%
SetBatchLines, -1

; 等待系统稳定
Sleep, 500

; 用 GDI+ 截图
output := A_WorkingDir . "\\_desktop_screenshot.png"

; 使用内置方式：PrintScreen 到剪贴板再保存
Send, {PrintScreen}
Sleep, 300

; 用 PowerShell 保存剪贴板图片
RunWait, powershell -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.Clipboard]::GetImage().Save('%output%', System.Drawing.Imaging.ImageFormat::Png)", , Hide

FileAppend, Done: %output%`n, %A_WorkingDir%\\_screenshot_log.txt
