@echo off
chcp 65001 > nul
echo ======================================================================
echo 🚀 智学伴 LearnMate AI Agent OS v3.0 — Windows 1440x900 原生桌面软件中枢
echo ======================================================================

set PYTHON_EXE=d:\AI_Work\.venv\Scripts\python.exe

echo ⚡ 正在启动 8 大 Agent 全功能 Windows 原生 GUI 桌面客户端...
cd /d "d:\AI_Work\人工智能大赛"
%PYTHON_EXE% desktop_app.py

if %ERRORLEVEL% NEQ 0 (
    echo ❌ 桌面端运行异常，请检查配置。
    pause
)
