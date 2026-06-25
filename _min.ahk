#NoEnv
SetBatchLines, -1
SetTitleMatchMode, 2

; 最小化所有 Chrome 窗口
WinMinimize, ahk_class Chrome_WidgetWin_1
Sleep, 200
WinMinimize, ahk_class Chrome_WidgetWin_1

; 也尝试 Minimize
Loop, 5 {
    WinMinimize, A
    Sleep, 100
}

Sleep, 300
