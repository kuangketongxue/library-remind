; 只缩小 Open Browser 窗口
#NoEnv
SetWorkingDir, %A_WorkingDir%
SetBatchLines, -1
SetTitleMatchMode, 2

; 只最小化特定窗口
WinMinimize, ahk_class Chrome_WidgetWin_1
Sleep, 100
WinMinimize, ahk_class Chrome_WidgetWin_1
Sleep, 100
WinMinimize, Open Browser

Sleep, 300
FileAppend, Done`n, _minimize_log.txt
