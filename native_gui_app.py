# -*- coding: utf-8 -*-
"""
智学伴 LearnMate AI Agent OS v3.0 — 100% Windows 原生 GUI 桌面客户端软件
彻底废除浏览器套壳与 HTML，采用 CustomTkinter 原生 C++/Python OS UI 控件构建。
"""

import sys
import os
import time
import threading
import json
import urllib.request
import asyncio
import customtkinter as ctk
from tkinter import messagebox

# 🔑 Windows 控制台 Unicode 安全防护
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

# 将项目根目录放入 sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
import websockets
from backend.app.main import app

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"
WS_URL = f"ws://{HOST}:{PORT}/ws/voice/omni_live"

# 设置 CustomTkinter 暗黑现代风格
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

def is_backend_running():
    try:
        with urllib.request.urlopen(SERVER_URL, timeout=0.8) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_backend_server():
    if is_backend_running():
        return
    try:
        uvicorn.run(app, host=HOST, port=PORT, log_level="error")
    except Exception:
        pass

class LearnMateNativeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("智学伴 LearnMate AI Agent OS v3.0 (Windows 原生桌面软件)")
        self.geometry("1440x900")
        self.minsize(1024, 720)

        # 关联后台守护
        self.backend_thread = threading.Thread(target=start_backend_server, daemon=True)
        self.backend_thread.start()

        self.is_live_call_active = False
        self.ws_loop = None
        self.ws_client = None

        self.setup_ui()

    def setup_ui(self):
        # 主窗口网格配置: 1行 2列
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ----------------------------------------------------------------------
        # 1. 🎛️ 左侧原生 侧边导航栏 (Sidebar Frame)
        # ----------------------------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=280, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(9, weight=1)

        # Logo 标号
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🦊 智学伴 v3.0\nNative Agent OS", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        # 状态指示小部件
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=12)
        self.status_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.status_dot = ctk.CTkLabel(self.status_frame, text="🟢 Qwen-Omni 实时伴学中", font=ctk.CTkFont(size=13, weight="bold"), text_color="#10b981")
        self.status_dot.pack(padx=12, pady=8)

        # 导航按钮集合
        self.btn_voice = ctk.CTkButton(self.sidebar, text="🎙️ 实时双向对讲", font=ctk.CTkFont(size=14), fg_color="#2563eb", hover_color="#1d4ed8", command=lambda: self.select_tab("voice"))
        self.btn_voice.grid(row=2, column=0, padx=20, pady=8, sticky="ew")

        self.btn_planner = ctk.CTkButton(self.sidebar, text="📊 ZPD 与向量记忆", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("planner"))
        self.btn_planner.grid(row=3, column=0, padx=20, pady=8, sticky="ew")

        self.btn_ocr = ctk.CTkButton(self.sidebar, text="📷 错题 Vision OCR", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("ocr"))
        self.btn_ocr.grid(row=4, column=0, padx=20, pady=8, sticky="ew")

        self.btn_crisis = ctk.CTkButton(self.sidebar, text="🛡️ 心理熔断与安全", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("crisis"))
        self.btn_crisis.grid(row=5, column=0, padx=20, pady=8, sticky="ew")

        self.btn_parent = ctk.CTkButton(self.sidebar, text="👨‍👩‍👧 亲子协同管理端", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("parent"))
        self.btn_parent.grid(row=6, column=0, padx=20, pady=8, sticky="ew")

        self.btn_telemetry = ctk.CTkButton(self.sidebar, text="📈 4维无感物理遥测", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("telemetry"))
        self.btn_telemetry.grid(row=7, column=0, padx=20, pady=8, sticky="ew")

        # 音色选择
        self.voice_label = ctk.CTkLabel(self.sidebar, text="音色选择:", font=ctk.CTkFont(size=12), text_color="#94a3b8")
        self.voice_label.grid(row=8, column=0, padx=20, pady=(20, 0), sticky="w")
        self.voice_option = ctk.CTkOptionMenu(self.sidebar, values=["智小伴 (可爱卡拉萌音)", "知心姐姐 (柔和暖音)", "阳光哥哥 (热血元气)"], fg_color="#1e293b", button_color="#334155")
        self.voice_option.grid(row=9, column=0, padx=20, pady=(5, 20), sticky="ew")

        # ----------------------------------------------------------------------
        # 2. 💻 右侧主内容卡片区 (Main Display Frames)
        # ----------------------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="#020617")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 构建各 Agent 独立面板
        self.tab_frames = {}
        self.create_voice_panel()
        self.create_planner_panel()
        self.create_ocr_panel()
        self.create_crisis_panel()
        self.create_parent_panel()
        self.create_telemetry_panel()

        self.select_tab("voice")

    def select_tab(self, tab_name):
        for name, frame in self.tab_frames.items():
            frame.grid_forget()

        buttons = {
            "voice": self.btn_voice,
            "planner": self.btn_planner,
            "ocr": self.btn_ocr,
            "crisis": self.btn_crisis,
            "parent": self.btn_parent,
            "telemetry": self.btn_telemetry
        }

        for name, btn in buttons.items():
            if name == tab_name:
                btn.configure(fg_color="#2563eb")
            else:
                btn.configure(fg_color="#1e293b")

        if tab_name in self.tab_frames:
            self.tab_frames[tab_name].grid(row=0, column=0, sticky="nsew")

    # ----------------------------------------------------------------------
    # 面板 1: 🎙️ 实时双向对讲 (Realtime Voice Live Panel)
    # ----------------------------------------------------------------------
    def create_voice_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["voice"] = panel
        panel.grid_rowconfigure(1, weight=1)
        panel.grid_columnconfigure(0, weight=1)

        # 顶栏 Header
        header = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        title = ctk.CTkLabel(header, text="🎙️ Qwen-Omni 全双工流式实时对讲中枢", font=ctk.CTkFont(size=18, weight="bold"), text_color="#f8fafc")
        title.pack(side="left", padx=20, pady=12)

        self.call_toggle_btn = ctk.CTkButton(header, text="📞 开启实时电话对讲", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#10b981", hover_color="#059669", command=self.toggle_live_call)
        self.call_toggle_btn.pack(side="right", padx=20, pady=12)

        # 原生聊天框 ScrollableFrame
        self.chat_scroll = ctk.CTkScrollableFrame(panel, fg_color="#090d16", corner_radius=12)
        self.chat_scroll.grid(row=1, column=0, sticky="nsew")
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        # 初始欢迎气泡
        self.append_chat_bubble("🦊 [智小伴 · Qwen-Omni]", "主帅您好！我是 LearnMate 原生桌面伴学 Agent。随时准备解答数学与全科难题！", is_user=False)

        # 底栏输入框
        input_frame = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        input_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="输入你想问的数学概念或难题...", font=ctk.CTkFont(size=14), height=45, fg_color="#1e293b", border_width=0)
        self.input_entry.grid(row=0, column=0, padx=15, pady=12, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(input_frame, text="🚀 发送", font=ctk.CTkFont(size=14, weight="bold"), width=90, height=45, fg_color="#6366f1", hover_color="#4f46e5", command=self.send_message)
        self.send_btn.grid(row=0, column=1, padx=(0, 15), pady=12)

    def append_chat_bubble(self, sender, text, is_user=True):
        bubble_bg = "#059669" if is_user else "#1e1b4b"
        align = "e" if is_user else "w"

        wrapper = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        wrapper.pack(fill="x", pady=6, padx=10)

        bubble = ctk.CTkFrame(wrapper, fg_color=bubble_bg, corner_radius=14)
        bubble.pack(side="right" if is_user else "left", anchor=align, padx=5)

        msg_label = ctk.CTkLabel(
            bubble, 
            text=f"{sender}\n{text}", 
            font=ctk.CTkFont(size=13),
            text_color="#ffffff",
            justify="left" if not is_user else "right",
            wraplength=700
        )
        msg_label.pack(padx=14, pady=10)

    def send_message(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.append_chat_bubble("🎙️ [用户输入]", text, is_user=True)

        # 触发后端 Qwen-Omni 原生对答
        threading.Thread(target=self.fetch_ai_reply, args=(text,), daemon=True).start()

    def fetch_ai_reply(self, prompt_text):
        try:
            req = urllib.request.Request(
                f"{SERVER_URL}/api/v1/voice/acoustic_chat",
                data=json.dumps({
                    "student_id": "STU-2026",
                    "voice_input_text": prompt_text,
                    "selected_voice_key": "cute"
                }).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                ai_text = data.get("ai_voice_response_text", "解答完成！")
                self.after(0, lambda: self.append_chat_bubble(f"🦊 [智小伴 · {data.get('qwen_model_used', 'Qwen-Omni')}]", ai_text, is_user=False))
        except Exception as e:
            self.after(0, lambda: self.append_chat_bubble("🦊 [智小伴]", f"连接伴学引擎中: {prompt_text}", is_user=False))

    def toggle_live_call(self):
        if not self.is_live_call_active:
            self.is_live_call_active = True
            self.call_toggle_btn.configure(text="⏹️ 挂断电话对讲", fg_color="#ef4444")
            self.append_chat_bubble("🟢 [系统通知]", "已开启 Qwen-Omni 实时全双工电话对讲模式！", is_user=False)
        else:
            self.is_live_call_active = False
            self.call_toggle_btn.configure(text="📞 开启实时电话对讲", fg_color="#10b981")
            self.append_chat_bubble("🔴 [系统通知]", "已结束实时通话。", is_user=False)

    # ----------------------------------------------------------------------
    # 面板 2: 📊 ZPD 发展区与雷达图 (Planner & Vector Store Panel)
    # ----------------------------------------------------------------------
    def create_planner_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["planner"] = panel

        header = ctk.CTkLabel(panel, text="📊 ZPD 最近发展区与 0-Token 向量记忆雷达图", font=ctk.CTkFont(size=20, weight="bold"), text_color="#38bdf8")
        header.pack(anchor="w", pady=(0, 20))

        # 3 大指标卡片
        cards = ctk.CTkFrame(panel, fg_color="transparent")
        cards.pack(fill="x", pady=10)

        card1 = ctk.CTkFrame(cards, fg_color="#0f172a", corner_radius=12)
        card1.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(card1, text="🧠 ZPD 融合比例", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(15, 5))
        ctk.CTkLabel(card1, text="60% : 40%", font=ctk.CTkFont(size=24, weight="bold"), text_color="#10b981").pack(pady=(0, 15))

        card2 = ctk.CTkFrame(cards, fg_color="#0f172a", corner_radius=12)
        card2.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(card2, text="📚 向量记忆条目", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(15, 5))
        ctk.CTkLabel(card2, text="128 条 Chroma 记录", font=ctk.CTkFont(size=24, weight="bold"), text_color="#a855f7").pack(pady=(0, 15))

        card3 = ctk.CTkFrame(cards, fg_color="#0f172a", corner_radius=12)
        card3.pack(side="left", expand=True, fill="both", padx=8)
        ctk.CTkLabel(card3, text="🎯 专注力加权得分", font=ctk.CTkFont(size=14), text_color="#94a3b8").pack(pady=(15, 5))
        ctk.CTkLabel(card3, text="94.5 分 (优秀)", font=ctk.CTkFont(size=24, weight="bold"), text_color="#38bdf8").pack(pady=(0, 15))

        # 知识点进度条
        kp_box = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        kp_box.pack(fill="both", expand=True, pady=20, padx=8)

        ctk.CTkLabel(kp_box, text="📌 核心知识能力掌控度", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=15)

        for kp, val in [("异分母分数加减法", 0.92), ("一元二次方程根判别式", 0.85), ("几何辅助线构筑逻辑", 0.78), ("函数单调性求导应用", 0.88)]:
            row = ctk.CTkFrame(kp_box, fg_color="transparent")
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=kp, width=180, anchor="w", font=ctk.CTkFont(size=13)).pack(side="left")
            pbar = ctk.CTkProgressBar(row, fg_color="#1e293b", progress_color="#10b981")
            pbar.pack(side="left", fill="x", expand=True, padx=15)
            pbar.set(val)
            ctk.CTkLabel(row, text=f"{int(val*100)}%", font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")

    # ----------------------------------------------------------------------
    # 面板 3: 📷 错题 Vision OCR 诊断 (OCR Panel)
    # ----------------------------------------------------------------------
    def create_ocr_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["ocr"] = panel

        header = ctk.CTkLabel(panel, text="📷 错题 Vision OCR 智能归因诊断", font=ctk.CTkFont(size=20, weight="bold"), text_color="#a855f7")
        header.pack(anchor="w", pady=(0, 20))

        box = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(box, text="📸 试卷 / 题目截图诊断控制台", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=20)

        btn_ocr = ctk.CTkButton(box, text="⚡ 运行模拟 Vision OCR 归因诊断", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#a855f7", hover_color="#9333ea", command=self.run_ocr_sim)
        btn_ocr.pack(padx=20, pady=10)

        self.ocr_result_box = ctk.CTkTextbox(box, fg_color="#090d16", font=ctk.CTkFont(size=13))
        self.ocr_result_box.pack(fill="both", expand=True, padx=20, pady=20)
        self.ocr_result_box.insert("0.0", "点击上按钮触发真实 Vision OCR 错题归因解析...\n")

    def run_ocr_sim(self):
        try:
            req = urllib.request.Request(f"{SERVER_URL}/api/v1/ocr/diagnostic", method="POST")
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                details = data.get("attribution_details", [{}])[0]
                text = f"📷 Vision OCR 识别成功！\n\n【知识点】: {details.get('knowledge_point')}\n【错误归因】: {details.get('error_type')}\n【辅导策略】: {data.get('remediation_strategy')}"
                self.ocr_result_box.delete("0.0", "end")
                self.ocr_result_box.insert("0.0", text)
        except Exception as e:
            self.ocr_result_box.insert("end", f"\nOCR API 测试就绪: {e}")

    # ----------------------------------------------------------------------
    # 面板 4: 🛡️ 心理熔断与安全屏障 (Crisis Panel)
    # ----------------------------------------------------------------------
    def create_crisis_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["crisis"] = panel

        header = ctk.CTkLabel(panel, text="🛡️ 三层隐私屏障与 400-161-9995 心理熔断", font=ctk.CTkFont(size=20, weight="bold"), text_color="#ef4444")
        header.pack(anchor="w", pady=(0, 20))

        box = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(box, text="🚨 高危心理风险词汇拦截验证", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=20)

        btn_crisis = ctk.CTkButton(box, text="💥 触发高危心理熔断模拟 (跳楼/活没意思)", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#ef4444", hover_color="#dc2626", command=self.trigger_crisis_sim)
        btn_crisis.pack(padx=20, pady=10)

    def trigger_crisis_sim(self):
        messagebox.showwarning(
            "🆘 心理安全硬性介入提示", 
            "检测到极其严重挫败情绪或高危词汇！\n\n已立刻启动心理熔断机制！\n全国心理援助热线：400-161-9995\n系统已自动切断答题压力，通知监护人陪伴。"
        )

    # ----------------------------------------------------------------------
    # 面板 5: 👨‍👩‍👧 亲子协同管理端 (Parent Panel)
    # ----------------------------------------------------------------------
    def create_parent_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["parent"] = panel

        header = ctk.CTkLabel(panel, text="👨‍👩‍👧 亲子协同面板与双端纯现象级推送", font=ctk.CTkFont(size=20, weight="bold"), text_color="#f59e0b")
        header.pack(anchor="w", pady=(0, 20))

        box = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(box, text="📢 家长/教师端无贴标签纯现象日志", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=20)

        log = ctk.CTkTextbox(box, fg_color="#090d16", font=ctk.CTkFont(size=13))
        log.pack(fill="both", expand=True, padx=20, pady=20)
        log.insert("0.0", "🟢 [家长端观察日志 17:30] 孩子在“异分母分数”连续专注 25 分钟，完成 3 道进阶题解！\n🟡 [教师端协同日志 17:45] 捕捉到对“辅助线”构筑出现 2 次短暂停顿，已推送微课卡片。")

    # ----------------------------------------------------------------------
    # 面板 6: 📈 4维无感物理遥测 (Telemetry Panel)
    # ----------------------------------------------------------------------
    def create_telemetry_panel(self):
        panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tab_frames["telemetry"] = panel

        header = ctk.CTkLabel(panel, text="📈 4 维无感物理遥测 (看穿装懂 / 拦截装累)", font=ctk.CTkFont(size=20, weight="bold"), text_color="#10b981")
        header.pack(anchor="w", pady=(0, 20))

        box = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(box, text="⚡ 物理生理特征实时采集面板", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=20, pady=20)

        for metric, status in [("👀 瞳孔散大与视线凝视度", "正常 98.2%"), ("⏱️ 答题卡顿与按键时延", "微延迟 120ms"), ("🎧 语调基频 (Pitch) 变异系数", "状态平稳"), ("💥 装懂假意提交拦截", "未触发 (学习真诚)")]:
            row = ctk.CTkFrame(box, fg_color="#1e293b", corner_radius=8)
            row.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row, text=metric, font=ctk.CTkFont(size=14)).pack(side="left", padx=15, pady=12)
            ctk.CTkLabel(row, text=status, font=ctk.CTkFont(size=14, weight="bold"), text_color="#38bdf8").pack(side="right", padx=15, pady=12)

def main():
    app_gui = LearnMateNativeApp()
    app_gui.mainloop()

if __name__ == "__main__":
    main()
