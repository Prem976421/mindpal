Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "C:\Users\PREM MOTGHARE\Desktop\mindpal"
WshShell.Run "cmd.exe /c launch_mindpal.bat", 0, False
