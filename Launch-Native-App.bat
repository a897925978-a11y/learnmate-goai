@echo off
chcp 65001 > nul
echo ======================================================================
echo 🚀 智学伴 LearnMate AI Agent OS v3.0 — 100% 纯原生 Windows 桌面客户端软件
echo ======================================================================

set PYTHON_EXE=d:\AI_Work\.venv\Scripts\pythonw.exe

cd /d "d:\AI_Work\人工智能大赛"
start "" "%PYTHON_EXE%" native_gui_app.py
