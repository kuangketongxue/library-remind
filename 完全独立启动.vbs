' 完全独立启动脚本 - 确保关闭终端后程序继续运行
Set WshShell = CreateObject("WScript.Shell")

' 使用 pythonw（无窗口Python）启动程序
' 参数说明：
' - 第一个参数：要执行的命令
' - 第二个参数 0：隐藏窗口
' - 第三个参数 False：不等待程序结束，立即返回
WshShell.Run "pythonw rest_reminder.py --silent", 0, False

Set WshShell = Nothing
