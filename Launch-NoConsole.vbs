Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "d:\AI_Work\人工智能大赛"
WshShell.Run "d:\AI_Work\.venv\Scripts\pythonw.exe desktop_app.py", 0, False
