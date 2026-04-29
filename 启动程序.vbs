Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "pythonw rest_reminder.py", 0, False
Set WshShell = Nothing
