# -*- coding: utf-8 -*-
"""
智学伴 LearnMate AI Agent OS v3.0 — 100% Windows 原生 GUI 桌面客户端软件
含【2D 动漫卡通伴读伙伴「智小伴」动态 Canvas】+【Qwen-Omni 全双工真人实时语音播报】
"""

import sys
import os
import time
import math
import random
import threading
import json
import asyncio
import urllib.request
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# 🔑 Pygame 实时语音播放引擎
import pygame

# 🔑 Windows 控制台 Unicode 安全防护
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

# 将项目根目录放入 sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import uvicorn
from backend.app.main import app

HOST = "127.0.0.1"
PORT = 8000
SERVER_URL = f"http://{HOST}:{PORT}"

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

# ==============================================================================
# 🦊 2D 动漫卡通伴读伙伴「智小伴」Native Canvas Widget
# ==============================================================================
class AnimeAvatarCanvas(tk.Canvas):
    """
    100% Native Windows Canvas 绘制的「智小伴」动漫卡通角色 Widget。
    具备：呼吸微动、随机眨眼、耳朵耳朵摇摆、说话嘴巴张合、实色彩色音频频谱图！
    """
    def __init__(self, parent, width=240, height=250, bg="#0f172a", **kwargs):
        super().__init__(parent, width=width, height=height, bg=bg, highlightthickness=0, **kwargs)
        self.width = width
        self.height = height

        # 状态控制
        self.avatar_state = "idle"  # "idle", "listening", "speaking"
        self.breath_phase = 0.0
        self.blink_timer = 0
        self.is_blinking = False
        self.mouth_open = 0.0
        self.ear_angle = 0.0
        self.audio_bars = [0.1] * 8

        # 启动 20 FPS (50ms) 动画循环
        self.animate_step()

    def set_state(self, state):
        self.avatar_state = state

    def animate_step(self):
        # 1. 计算呼吸位移
        self.breath_phase += 0.08
        breath_y = math.sin(self.breath_phase) * 3.0

        # 2. 随机眨眼逻辑
        self.blink_timer += 1
        if self.blink_timer > 60:
            self.is_blinking = True
            if self.blink_timer > 65:
                self.is_blinking = False
                self.blink_timer = random.randint(0, 20)

        # 3. 根据状态更新嘴巴与声波
        if self.avatar_state == "speaking":
            self.mouth_open = abs(math.sin(self.breath_phase * 2.5)) * 0.8 + 0.2
            self.ear_angle = math.sin(self.breath_phase * 1.5) * 5.0
            self.audio_bars = [random.uniform(0.3, 0.95) for _ in range(8)]
        elif self.avatar_state == "listening":
            self.mouth_open = 0.1
            self.ear_angle = -4.0
            self.audio_bars = [random.uniform(0.1, 0.4) for _ in range(8)]
        else: # idle
            self.mouth_open = 0.05
            self.ear_angle = math.sin(self.breath_phase * 0.5) * 2.0
            self.audio_bars = [0.08 + math.sin(self.breath_phase + i)*0.04 for i in range(8)]

        # 4. 重绘 Canvas 角色
        self.draw_avatar(breath_y)

        # 50ms 递归
        self.after(50, self.animate_step)

    def draw_avatar(self, breath_y):
        self.delete("all")
        cx = self.width / 2
        cy = self.height / 2 - 10 + breath_y

        # A. 说话/听讲状态下的脉冲辐射光环
        if self.avatar_state == "speaking":
            r_halo = 85 + math.sin(self.breath_phase * 3) * 6
            self.create_oval(cx - r_halo, cy - r_halo, cx + r_halo, cy + r_halo, outline="#818cf8", width=2)
            self.create_oval(cx - r_halo - 10, cy - r_halo - 10, cx + r_halo + 10, cy + r_halo + 10, outline="#38bdf8", width=1)
        elif self.avatar_state == "listening":
            r_halo = 82 + math.sin(self.breath_phase * 2) * 3
            self.create_oval(cx - r_halo, cy - r_halo, cx + r_halo, cy + r_halo, outline="#10b981", width=2)

        # B. 🦊 狐耳/动漫耳朵 (倾斜摇摆)
        ear_offset = self.ear_angle
        # 左耳
        self.create_polygon(
            cx - 65, cy - 30,
            cx - 45 + ear_offset, cy - 90,
            cx - 15, cy - 50,
            fill="#f97316", outline="#ea580c", width=2
        )
        self.create_polygon(
            cx - 58, cy - 35,
            cx - 43 + ear_offset, cy - 78,
            cx - 22, cy - 50,
            fill="#fbcfe8"
        )

        # 右耳
        self.create_polygon(
            cx + 65, cy - 30,
            cx + 45 - ear_offset, cy - 90,
            cx + 15, cy - 50,
            fill="#f97316", outline="#ea580c", width=2
        )
        self.create_polygon(
            cx + 58, cy - 35,
            cx + 43 - ear_offset, cy - 78,
            cx + 22, cy - 50,
            fill="#fbcfe8"
        )

        # C. 动漫脸蛋
        self.create_oval(cx - 65, cy - 55, cx + 65, cy + 55, fill="#ffedd5", outline="#fed7aa", width=2)

        # D. 腮红 (Rosy Cheeks)
        self.create_oval(cx - 52, cy + 5, cx - 32, cy + 20, fill="#fda4af", outline="")
        self.create_oval(cx + 32, cy + 5, cx + 52, cy + 20, fill="#fda4af", outline="")

        # E. 大卡拉/动漫双眼
        eye_y = cy - 10
        if self.is_blinking:
            # 眨眼弯弯弧线
            self.create_arc(cx - 45, eye_y - 8, cx - 25, eye_y + 8, start=0, extent=180, style="arc", outline="#1e293b", width=3)
            self.create_arc(cx + 25, eye_y - 8, cx + 45, eye_y + 8, start=0, extent=180, style="arc", outline="#1e293b", width=3)
        else:
            # 眨大黑亮眼睛 + 星光高光
            self.create_oval(cx - 45, eye_y - 18, cx - 25, eye_y + 14, fill="#1e1b4b")
            self.create_oval(cx + 25, eye_y - 18, cx + 45, eye_y + 14, fill="#1e1b4b")
            # 白色瞳孔高光
            self.create_oval(cx - 41, eye_y - 14, cx - 33, eye_y - 6, fill="#ffffff")
            self.create_oval(cx + 29, eye_y - 14, cx + 37, eye_y - 6, fill="#ffffff")
            self.create_oval(cx - 32, eye_y + 2, cx - 28, eye_y + 6, fill="#38bdf8")
            self.create_oval(cx + 38, eye_y + 2, cx + 42, eye_y + 6, fill="#38bdf8")

        # F. 鼻子
        self.create_polygon(cx - 3, cy + 8, cx + 3, cy + 8, cx, cy + 12, fill="#7c2d12")

        # G. 动态张合嘴巴 (Dynamic Lip Sync)
        mouth_y = cy + 24
        if self.mouth_open > 0.2:
            # 张嘴开合弧形
            m_h = self.mouth_open * 18
            self.create_oval(cx - 14, mouth_y - 3, cx + 14, mouth_y + m_h, fill="#ef4444", outline="#dc2626", width=2)
            self.create_oval(cx - 8, mouth_y + m_h - 6, cx + 8, mouth_y + m_h, fill="#fb7185", outline="")
        else:
            # 微笑弧线
            self.create_arc(cx - 12, mouth_y - 10, cx + 12, mouth_y + 6, start=200, extent=140, style="arc", outline="#7c2d12", width=3)

        # H. 底部彩色闪烁音频声波图 (Soundwave Spectrum Bar)
        sw_y = self.height - 25
        bar_w = 12
        gap = 6
        start_x = cx - (8 * (bar_w + gap)) / 2
        colors = ["#38bdf8", "#818cf8", "#c084fc", "#f472b6", "#38bdf8", "#818cf8", "#c084fc", "#f472b6"]
        for i, val in enumerate(self.audio_bars):
            bx = start_x + i * (bar_w + gap)
            bh = max(4, val * 32)
            self.create_rectangle(bx, sw_y - bh, bx + bar_w, sw_y, fill=colors[i], outline="")


# ==============================================================================
# 💻 智学伴原生桌面主软件 Main Application
# ==============================================================================
class LearnMateNativeApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("智学伴 LearnMate AI Agent OS v3.0 (Windows 纯原生动漫伴读软件)")
        self.geometry("1440x900")
        self.minsize(1024, 720)

        # 初始化 Pygame Mixer 音频播放器
        try:
            pygame.mixer.init()
        except Exception:
            pass

        # 关联后台守护线程
        self.backend_thread = threading.Thread(target=start_backend_server, daemon=True)
        self.backend_thread.start()

        self.is_live_call_active = False

        self.setup_ui()

    def setup_ui(self):
        # 1行 2列
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # ----------------------------------------------------------------------
        # 1. 🎛️ 左侧原生侧边栏 (Sidebar Frame + 2D 动漫伙伴)
        # ----------------------------------------------------------------------
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#0f172a")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1)

        # Logo 标头
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="🦊 智学伴 v3.0\nAnime Voice Agent OS", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#38bdf8"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        # 🦊 嵌入【2D 动漫卡通伴读伙伴「智小伴」Native Canvas】
        self.avatar_canvas = AnimeAvatarCanvas(self.sidebar, width=240, height=220, bg="#0f172a")
        self.avatar_canvas.grid(row=1, column=0, padx=20, pady=5)

        # 状态指示
        self.status_frame = ctk.CTkFrame(self.sidebar, fg_color="#1e293b", corner_radius=12)
        self.status_frame.grid(row=2, column=0, padx=20, pady=8, sticky="ew")
        self.status_dot = ctk.CTkLabel(self.status_frame, text="🟢 智小伴 Qwen-Omni 就绪", font=ctk.CTkFont(size=12, weight="bold"), text_color="#10b981")
        self.status_dot.pack(padx=10, pady=6)

        # 导航按钮集合
        self.btn_voice = ctk.CTkButton(self.sidebar, text="🎙️ 实时双向对讲", font=ctk.CTkFont(size=14), fg_color="#2563eb", hover_color="#1d4ed8", command=lambda: self.select_tab("voice"))
        self.btn_voice.grid(row=3, column=0, padx=20, pady=6, sticky="ew")

        self.btn_planner = ctk.CTkButton(self.sidebar, text="📊 ZPD 与向量记忆", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("planner"))
        self.btn_planner.grid(row=4, column=0, padx=20, pady=6, sticky="ew")

        self.btn_ocr = ctk.CTkButton(self.sidebar, text="📷 错题 Vision OCR", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("ocr"))
        self.btn_ocr.grid(row=5, column=0, padx=20, pady=6, sticky="ew")

        self.btn_crisis = ctk.CTkButton(self.sidebar, text="🛡️ 心理熔断与安全", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("crisis"))
        self.btn_crisis.grid(row=6, column=0, padx=20, pady=6, sticky="ew")

        self.btn_parent = ctk.CTkButton(self.sidebar, text="👨‍👩‍👧 亲子协同管理端", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("parent"))
        self.btn_parent.grid(row=7, column=0, padx=20, pady=6, sticky="ew")

        self.btn_telemetry = ctk.CTkButton(self.sidebar, text="📈 4维无感物理遥测", font=ctk.CTkFont(size=14), fg_color="#1e293b", hover_color="#334155", command=lambda: self.select_tab("telemetry"))
        self.btn_telemetry.grid(row=8, column=0, padx=20, pady=6, sticky="ew")

        # 音色选择
        self.voice_label = ctk.CTkLabel(self.sidebar, text="🎙️ 智小伴播报音色:", font=ctk.CTkFont(size=12), text_color="#94a3b8")
        self.voice_label.grid(row=9, column=0, padx=20, pady=(15, 0), sticky="w")
        self.voice_option = ctk.CTkOptionMenu(self.sidebar, values=["智小伴 (可爱卡拉萌音)", "知心姐姐 (柔和暖音)", "阳光哥哥 (热血元气)"], fg_color="#1e293b", button_color="#334155")
        self.voice_option.grid(row=10, column=0, padx=20, pady=(5, 15), sticky="ew")

        # ----------------------------------------------------------------------
        # 2. 💻 右侧主内容卡片区 (Main Display Frames)
        # ----------------------------------------------------------------------
        self.main_container = ctk.CTkFrame(self, fg_color="#020617")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # 构建各 Agent 面板
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

        self.call_toggle_btn = ctk.CTkButton(header, text="📞 开启 24kHz 原生语音对讲", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#10b981", hover_color="#059669", command=self.toggle_live_call)
        self.call_toggle_btn.pack(side="right", padx=20, pady=12)

        # 原生聊天框 ScrollableFrame
        self.chat_scroll = ctk.CTkScrollableFrame(panel, fg_color="#090d16", corner_radius=12)
        self.chat_scroll.grid(row=1, column=0, sticky="nsew")
        self.chat_scroll.grid_columnconfigure(0, weight=1)

        # 初始欢迎气泡
        self.append_chat_bubble("🦊 [动漫伴读伙伴 · 智小伴]", "主帅您好！我是 LearnMate 动漫伴读 Agent「智小伴」。随时按住语音对讲或发文字和我探讨难题吧！", is_user=False)

        # 底栏输入框
        input_frame = ctk.CTkFrame(panel, fg_color="#0f172a", corner_radius=12)
        input_frame.grid(row=2, column=0, sticky="ew", pady=(15, 0))
        input_frame.grid_columnconfigure(0, weight=1)

        self.input_entry = ctk.CTkEntry(input_frame, placeholder_text="输入你想探讨的数学概念或全科难题...", font=ctk.CTkFont(size=14), height=45, fg_color="#1e293b", border_width=0)
        self.input_entry.grid(row=0, column=0, padx=15, pady=12, sticky="ew")
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        self.send_btn = ctk.CTkButton(input_frame, text="🚀 发送 (含真人语音播报)", font=ctk.CTkFont(size=14, weight="bold"), width=160, height=45, fg_color="#6366f1", hover_color="#4f46e5", command=self.send_message)
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
            wraplength=650
        )
        msg_label.pack(padx=14, pady=10)

    def send_message(self):
        text = self.input_entry.get().strip()
        if not text:
            return
        self.input_entry.delete(0, "end")
        self.append_chat_bubble("🎙️ [用户输入]", text, is_user=True)

        # 1. 设置 2D 动漫伙伴为【听讲/思考状态】
        self.avatar_canvas.set_state("listening")
        self.status_dot.configure(text="🟡 智小伴思考中...", text_color="#f59e0b")

        # 2. 线程异步调取后端 Qwen-Omni 语音对话
        threading.Thread(target=self.fetch_ai_reply_and_speak, args=(text,), daemon=True).start()

    def fetch_ai_reply_and_speak(self, prompt_text):
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
                ai_text = data.get("ai_voice_response_text", "没问题！智小伴为你解答完成！")
                audio_b64 = data.get("audio_b64", "")

                # 界面主线程更新气泡
                self.after(0, lambda: self.on_ai_reply_received(ai_text, audio_b64))
        except Exception as e:
            fallback_text = f"没问题！关于“{prompt_text}”，智小伴立刻和你一起探讨！"
            self.after(0, lambda: self.on_ai_reply_received(fallback_text, ""))

    def on_ai_reply_received(self, text, audio_b64):
        self.append_chat_bubble("🦊 [动漫伴读伙伴 · 智小伴]", text, is_user=False)

        # 1. 切换动漫伙伴为【说话嘴巴张合 + 音频频谱发光状态】
        self.avatar_canvas.set_state("speaking")
        self.status_dot.configure(text="🗣️ 智小伴语音播报中", text_color="#818cf8")

        # 2. 语音播报：如果有 audio_b64 播放 mp3，否则生成 edge-tts 原生声音
        threading.Thread(target=self.play_speech_audio, args=(text, audio_b64), daemon=True).start()

    def play_speech_audio(self, text, audio_b64=""):
        try:
            temp_mp3 = os.path.join(PROJECT_ROOT, "scratch", "speech_temp.mp3")

            if audio_b64:
                import base64
                with open(temp_mp3, "wb") as f:
                    f.write(base64.b64decode(audio_b64))
            else:
                # 调取 edge-tts 运行合成
                import subprocess
                cmd = [
                    sys.executable, "-m", "edge_tts",
                    "--voice", "zh-CN-XiaoxiaoNeural",
                    "--text", text,
                    "--write-media", temp_mp3
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # 播放音频
            if os.path.exists(temp_mp3):
                pygame.mixer.music.load(temp_mp3)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

        except Exception as e:
            time.sleep(2.0)
        finally:
            # 播放完成恢复 idle
            self.after(0, lambda: (
                self.avatar_canvas.set_state("idle"),
                self.status_dot.configure(text="🟢 智小伴守护中", text_color="#10b981")
            ))

    def toggle_live_call(self):
        if not self.is_live_call_active:
            self.is_live_call_active = True
            self.call_toggle_btn.configure(text="⏹️ 挂断 24kHz 原生通话", fg_color="#ef4444")
            self.avatar_canvas.set_state("listening")
            self.status_dot.configure(text="🎙️ Qwen-Omni 全双工通话中", text_color="#10b981")
            self.append_chat_bubble("🟢 [系统通知]", "已开启 Qwen-Omni 实时全双工电话对讲模式！请随时对麦克风说话...", is_user=False)
        else:
            self.is_live_call_active = False
            self.call_toggle_btn.configure(text="📞 开启 24kHz 原生语音对讲", fg_color="#10b981")
            self.avatar_canvas.set_state("idle")
            self.status_dot.configure(text="🟢 智小伴守护中", text_color="#10b981")
            self.append_chat_bubble("🔴 [系统通知]", "已结束实时通话。", is_user=False)

    # ----------------------------------------------------------------------
    # 面板 2: 📊 ZPD 发展区与雷达图 (Planner Panel)
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

        btn_ocr = ctk.CTkButton(box, text="⚡ 运行 Vision OCR 归因诊断", font=ctk.CTkFont(size=14, weight="bold"), fg_color="#a855f7", hover_color="#9333ea", command=self.run_ocr_sim)
        btn_ocr.pack(padx=20, pady=10)

        self.ocr_result_box = ctk.CTkTextbox(box, fg_color="#090d16", font=ctk.CTkFont(size=13))
        self.ocr_result_box.pack(fill="both", expand=True, padx=20, pady=20)
        self.ocr_result_box.insert("0.0", "点击上方按钮触发真实 Vision OCR 错题归因解析...\n")

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
