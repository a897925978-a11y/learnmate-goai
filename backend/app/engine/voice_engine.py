# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」通义千问 Qwen-Omni & Edge/CosyVoice 广播级神经网络【真人拟音 TTS 引擎 + 全身动漫助手】(voice_engine.py)

核心功能：
1. 🎙️ 广播级神经网络 Voice TTS 声学生成器 (Edge-TTS 24kHz 原生 MP3 声场流)：
   - `cute`: `zh-CN-XiaoxiaoNeural` (+40Hz Pitch) 萌系卡拉小狐狸
   - `sweet`: `zh-CN-XiaoyiNeural` (+15Hz Pitch) 知心姐姐温柔女声
   - `boy`: `zh-CN-YunxiNeural` (+0Hz Pitch) 阳光哥哥热血青年男声
   - `master`: `zh-CN-YunyangNeural` (-25Hz Pitch) 智囊导师沉稳教授低音
2. 🦊 全身动漫卡通助手「智小伴」姿态与主动介入中枢
"""

import os
import uuid
import requests
import json
import asyncio
import base64
import edge_tts
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.engine.world_model_engine import world_model_engine, get_dashscope_credentials
from backend.app.engine.vector_store import vector_store


class FullBodyMascotState(BaseModel):
    avatar_key: str = "fox_buddy"
    avatar_name: str = "智小伴"
    avatar_emoji: str = "🦊"
    body_action: str = "idle"  # idle | proactive_jump | thinking | happy_cheer | calm_hug
    speech_prompt: str = ""
    glow_color: str = "#10b981"


class ProactiveCheckRequest(BaseModel):
    student_id: str = "STU-2026"
    idle_seconds: float = 0.0
    backspace_count: int = 0
    current_hour: int = 20
    current_concept: str = "异分母分数加减法"
    interest_anchor: str = "Minecraft"
    selected_voice_key: str = "cute"


class ProactiveCheckResponse(BaseModel):
    should_intervene: bool
    trigger_reason: str
    mascot_body_state: FullBodyMascotState
    proactive_speech_text: str
    audio_data_url: Optional[str] = None
    qwen_pedagogical_tip: str


class VoiceChatRequest(BaseModel):
    student_id: str = "STU-2026"
    voice_input_text: str = "你好"
    interest_anchor: str = "Minecraft"
    selected_voice_key: str = "cute"
    audio_wpm: float = 120.0
    audio_pause_s: float = 2.2


class VoiceChatResponse(BaseModel):
    session_id: str
    student_input_transcript: str
    ai_voice_response_text: str
    mascot_body_state: FullBodyMascotState
    speech_audio_wave_preset: List[float] = [0.35, 0.7, 0.9, 0.4, 0.85, 0.65, 0.95, 0.5, 0.8, 0.3]
    audio_data_url: Optional[str] = None
    qwen_model_used: str
    vector_memory_id: Optional[str] = None


VOICE_PRESETS = {
    "cute": {"voice": "zh-CN-XiaoxiaoNeural", "pitch": "+40Hz", "rate": "+15%"},
    "sweet": {"voice": "zh-CN-XiaoyiNeural", "pitch": "+15Hz", "rate": "-5%"},
    "boy": {"voice": "zh-CN-YunxiNeural", "pitch": "+0Hz", "rate": "+10%"},
    "master": {"voice": "zh-CN-YunyangNeural", "pitch": "-25Hz", "rate": "-10%"}
}


def generate_neural_tts_audio_data_url(text: str, voice_key: str = "cute") -> Optional[str]:
    """
    通过 24kHz 神经网络声学引擎将文本转换为 MP3 Base64 Data URL
    """
    preset = VOICE_PRESETS.get(voice_key, VOICE_PRESETS["cute"])
    try:
        async def _async_gen():
            communicate = edge_tts.Communicate(
                text=text,
                voice=preset["voice"],
                pitch=preset["pitch"],
                rate=preset["rate"]
            )
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            return audio_bytes

        # 在同步环境中安全运行 asyncio
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # 若在异步 Loop 内部，新建独立的 runner 运行
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                audio_bytes = pool.submit(lambda: asyncio.run(_async_gen())).result(timeout=8)
        else:
            audio_bytes = asyncio.run(_async_gen())

        if audio_bytes:
            b64_str = base64.b64encode(audio_bytes).decode('utf-8')
            return f"data:audio/mp3;base64,{b64_str}"
    except Exception as e:
        print("Neural TTS Generation Exception:", e)
    return None


class ProactiveVoiceAssistantEngine:
    """
    通义千问 Qwen 高保真【广播级神经网络真人 TTS + 全身动漫助手 + 主动介入伴学脑中枢】
    """
    def check_proactive_intervention(self, req: ProactiveCheckRequest) -> ProactiveCheckResponse:
        """
        根据学生的行为心流（卡顿时间、涂改次数、时间）主动决策是否弹跳介入！
        """
        # 1. 22:00 夜间熄灯守夜
        if req.current_hour >= 22 or req.current_hour < 6:
            speech = "小同学！太晚啦，眼睛需要休息咯！智小伴帮你在老师和家长端做好打卡啦，快去睡觉吧~"
            audio_url = generate_neural_tts_audio_data_url(speech, req.selected_voice_key)
            return ProactiveCheckResponse(
                should_intervene=True,
                trigger_reason="22:00 夜间健康保护",
                mascot_body_state=FullBodyMascotState(
                    avatar_key=req.selected_voice_key,
                    avatar_name="智小伴",
                    avatar_emoji="🦊",
                    body_action="calm_hug",
                    speech_prompt=speech,
                    glow_color="#f59e0b"
                ),
                proactive_speech_text=speech,
                audio_data_url=audio_url,
                qwen_pedagogical_tip="护眼防疲劳熄灯保护"
            )

        # 2. 静置卡顿 > 90s 主动关怀
        if req.idle_seconds >= 90.0:
            api_key, base_url, model_id = get_dashscope_credentials()
            qwen_tip = "小同学，我看你在题目上停顿超过 1.5 分钟啦！遇到纸老虎了吗？小伴用 Minecraft 通分动画帮帮你好不好？"
            
            if api_key and not api_key.startswith("your_"):
                try:
                    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                    payload = {
                        "model": model_id,
                        "messages": [
                            {"role": "system", "content": "你是 Cartoon 萌宠 AI 伴学小狐狸【智小伴】。学生在一道数学题上卡顿了 90 秒，请用 1 句话主动且生动地鼓励他，并提供小帮助。"},
                            {"role": "user", "content": f"学生卡顿题目：{req.current_concept}，兴趣：{req.interest_anchor}"}
                        ],
                        "max_tokens": 120
                    }
                    r = requests.post(f"{base_url.rstrip('/')}/chat/completions", headers=headers, json=payload, timeout=8)
                    if r.status_code == 200:
                        qwen_tip = r.json()["choices"][0]["message"]["content"]
                except Exception as e:
                    print("Qwen Proactive API error:", e)

            audio_url = generate_neural_tts_audio_data_url(qwen_tip, req.selected_voice_key)

            return ProactiveCheckResponse(
                should_intervene=True,
                trigger_reason="静置卡顿 > 90s 心流困境",
                mascot_body_state=FullBodyMascotState(
                    avatar_key=req.selected_voice_key,
                    avatar_name="智小伴",
                    avatar_emoji="🦊",
                    body_action="proactive_jump",
                    speech_prompt=qwen_tip,
                    glow_color="#10b981"
                ),
                proactive_speech_text=qwen_tip,
                audio_data_url=audio_url,
                qwen_pedagogical_tip=f"通义千问主动介入卡顿辅助 ({model_id})"
            )

        # 3. 频删涂改 > 3 次 主动介入
        if req.backspace_count >= 3:
            speech = f"检测到你连续涂改答案啦！别气馁，咱们在《{req.interest_anchor}》里找准最小公倍数，通分就轻松解决啦！"
            audio_url = generate_neural_tts_audio_data_url(speech, req.selected_voice_key)
            return ProactiveCheckResponse(
                should_intervene=True,
                trigger_reason="频删涂改 > 3次 难度过高",
                mascot_body_state=FullBodyMascotState(
                    avatar_key=req.selected_voice_key,
                    avatar_name="智小伴",
                    avatar_emoji="🦊",
                    body_action="thinking",
                    speech_prompt=speech,
                    glow_color="#6366f1"
                ),
                proactive_speech_text=speech,
                audio_data_url=audio_url,
                qwen_pedagogical_tip="降维算法辅导"
            )

        return ProactiveCheckResponse(
            should_intervene=False,
            trigger_reason="心流状态良好",
            mascot_body_state=FullBodyMascotState(avatar_key=req.selected_voice_key, body_action="idle"),
            proactive_speech_text="",
            audio_data_url=None,
            qwen_pedagogical_tip=""
        )

    def process_voice_interaction(self, req: VoiceChatRequest) -> VoiceChatResponse:
        session_id = f"QWEN-VOICE-{uuid.uuid4().hex[:8].upper()}"
        api_key, base_url, model_id = get_dashscope_credentials()
        ai_response = ""

        if api_key and not api_key.startswith("your_"):
            try:
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                system_prompt = (
                    f"你是智学伴全身 3D 动漫卡通助手【智小伴】🦊。语气极其萌趣生动，用 1-2 句话回答学生。"
                )
                payload = {
                    "model": model_id,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": req.voice_input_text}
                    ],
                    "max_tokens": 150,
                    "temperature": 0.7
                }
                res = requests.post(f"{base_url.rstrip('/')}/chat/completions", headers=headers, json=payload, timeout=10)
                if res.status_code == 200:
                    ai_response = res.json()["choices"][0]["message"]["content"]
            except Exception as e:
                print("DashScope API Call Error:", e)

        if not ai_response:
            if "你好" in req.voice_input_text:
                ai_response = f"嗷呜~ 你好呀小同学！我是你的全身动漫伴读助手智小伴 🦊！今天有什么数学心事或者题目想和智小伴聊聊吗？"
            else:
                ai_response = f"嗷呜~ 收到你的话啦！关于【{req.voice_input_text}】，结合《{req.interest_anchor}》来看，咱们一步步拆解，一定会越来越棒！"

        # 🔑 生成广播级 24kHz 神经网络 MP3 音频 Base64 流
        audio_url = generate_neural_tts_audio_data_url(ai_response, req.selected_voice_key)

        vec_id = f"KEY-BEHAVIOR-{uuid.uuid4().hex[:6].upper()}"
        vector_store.upsert_knowledge_memory(
            doc_id=vec_id,
            content=f"全身动漫助手交互：学生【{req.voice_input_text}】，AI回答【{ai_response[:30]}】",
            metadata={"student_id": req.student_id}
        )

        return VoiceChatResponse(
            session_id=session_id,
            student_input_transcript=req.voice_input_text,
            ai_voice_response_text=ai_response,
            mascot_body_state=FullBodyMascotState(
                avatar_key=req.selected_voice_key,
                avatar_name="智小伴",
                avatar_emoji="🦊",
                body_action="happy_cheer"
            ),
            audio_data_url=audio_url,
            qwen_model_used=model_id,
            vector_memory_id=vec_id
        )


voice_engine = ProactiveVoiceAssistantEngine()
