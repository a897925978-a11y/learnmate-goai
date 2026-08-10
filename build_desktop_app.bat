@echo off
chcp 65001 > nul
echo ======================================================================
echo 🚀 智学伴 LearnMate AI Agent OS v3.0 — 原生 Windows 桌面客户端编译打包
echo ======================================================================

set PYTHON_EXE=d:\AI_Work\.venv\Scripts\python.exe

echo 📦 正在调用 PyInstaller 进行全量单文件打包 (.exe)...
%PYTHON_EXE% -m PyInstaller --noconfirm LearnMate-Agent-OS.spec

echo.
if exist "dist\LearnMate-Agent-OS_v3.0.exe" (
    echo 🎉 成功交付 Windows 原生桌面软件：dist\LearnMate-Agent-OS_v3.0.exe
) else (
    echo ❌ 打包过程中出现异常，请检查构建日志。
)
pause
