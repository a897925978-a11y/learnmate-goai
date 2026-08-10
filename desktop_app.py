# -*- coding: utf-8 -*-
"""
智学伴 LearnMate AI Agent OS v3.0 — 原生 Windows 桌面客户端中枢 (Desktop Shell Launcher)
双击 EXE 或运行脚本直接启动本地 FastAPI 伴学引擎，并调起 Windows 1440x900 原生 GUI 窗口。
"""

import sys
import os
import time
import threading
import urllib.request
import subprocess

# 🔑 针对 Windows 控制台编码预防 UnicodeEncodeError 崩溃
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    try: sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

def safe_print(*args, **kwargs):
    """防止控制台打印 Emoji 引发 UnicodeEncodeError"""
    try:
        print(*args, **kwargs)
    except Exception:
        clean_args = [str(a).encode('ascii', 'ignore').decode('ascii') for a in args]
        print(*clean_args, **kwargs)

import uvicorn

# 将项目根目录放入 Python Path 搜寻范围
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"

def is_backend_running():
    try:
        with urllib.request.urlopen(SERVER_URL, timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_backend_server():
    """在后台线程中平滑拉起 Uvicorn FastAPI 服务"""
    if is_backend_running():
        safe_print(f"[LearnMate Desktop Shell] 检测到 Uvicorn 引擎已在运行: {SERVER_URL}")
        return
    safe_print(f"[LearnMate Desktop Shell] 启动本地伴学引擎: {SERVER_URL}...")
    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
    except Exception as e:
        safe_print(f"Uvicorn Server exception: {e}")

def wait_for_backend_ready():
    """等待后台 FastAPI 服务初始化就绪"""
    for _ in range(30):
        if is_backend_running():
            safe_print("[LearnMate Desktop Shell] FastAPI 后台引擎就绪！")
            return True
        time.sleep(0.2)
    return False

def launch_native_app_mode():
    """多重降级方案：调起 Microsoft Edge / Chrome 独立 App Mode 客户端窗口 (无标签/无地址栏)"""
    safe_print("[LearnMate Desktop Shell] 启动 Windows 原生 App Mode 桌面客户端 GUI...")
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        "msedge.exe"
    ]
    for exe in edge_paths:
        try:
            cmd = [exe, f"--app={SERVER_URL}", "--window-size=1440,900", "--user-data-dir=" + os.path.join(PROJECT_ROOT, "scratch", "edge_user_data")]
            proc = subprocess.Popen(cmd)
            proc.wait()
            return True
        except Exception:
            continue
    return False

def main():
    # 1. 启动后台 FastAPI Uvicorn 守护线程
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()

    # 2. 阻塞校验服务健康度
    wait_for_backend_ready()

    # 3. 尝试 PyWebView 调起 GUI，若失败自动降级至 Native App Mode
    try:
        import webview
        window = webview.create_window(
            title="智学伴 LearnMate AI Agent OS v3.0",
            url=SERVER_URL,
            width=1440,
            height=900,
            min_size=(1024, 720),
            resizable=True,
            text_select=True,
            confirm_close=False
        )
        safe_print("[LearnMate Desktop Shell] 正在拉起 Windows 1440x900 原生 GUI 窗口...")
        webview.start(debug=False)
        safe_print("[LearnMate Desktop Shell] 桌面客户端正常退出。")
    except Exception as e:
        safe_print(f"[LearnMate Desktop Shell] PyWebView 异常 ({e})，自动切换至 Edge App Mode 独立桌面应用窗口...")
        launch_native_app_mode()

if __name__ == "__main__":
    main()
