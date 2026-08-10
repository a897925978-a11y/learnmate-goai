# -*- coding: utf-8 -*-
"""
智学伴 LearnMate AI Agent OS v3.0 — 原生 Windows 桌面客户端中枢 (Desktop Shell Launcher)
双击 EXE 或运行脚本直接启动本地 FastAPI 伴学引擎，并调起 Windows 原生 WebView2 1440x900 桌面应用窗口。
"""

import sys
import os
import time
import threading
import urllib.request

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

import webview
import uvicorn

# 将项目根目录放入 Python Path 搜寻范围
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.app.main import app

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"

def start_backend_server():
    """在后台线程中平滑拉起 Uvicorn FastAPI 服务"""
    safe_print(f"[LearnMate Desktop Shell] 启动本地伴学引擎: {SERVER_URL}...")
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")

def wait_for_backend_ready():
    """等待后台 FastAPI 服务初始化就绪"""
    for _ in range(30):
        try:
            with urllib.request.urlopen(SERVER_URL, timeout=1) as resp:
                if resp.status == 200:
                    safe_print("[LearnMate Desktop Shell] FastAPI 后台引擎就绪！")
                    return True
        except Exception:
            time.sleep(0.2)
    return False

def main():
    # 1. 启动后台 FastAPI Uvicorn 守护线程
    server_thread = threading.Thread(target=start_backend_server, daemon=True)
    server_thread.start()

    # 2. 阻塞校验服务健康度
    wait_for_backend_ready()

    # 3. 创建原生 1440x900 Windows 桌面客户端窗口
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

    # 4. 启动 WebView2 原生桌面外壳
    safe_print("[LearnMate Desktop Shell] 正在拉起 Windows 1440x900 原生 GUI 窗口...")
    webview.start(gui='edgechromium', debug=False)
    safe_print("[LearnMate Desktop Shell] 桌面客户端正常退出。")

if __name__ == "__main__":
    main()
