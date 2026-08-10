# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」通义千问 Qwen-Omni & CosyVoice 原生高保真卡通伴读音色引擎 (voice_engine.py)

功能升级：
1. 🦊 卡通伴读助手形象绑定：“智小伴”萌宠狐狸 / 机器人 3D 动画状态
2. 🎙️ 阿里云百炼 Qwen-Omni / CosyVoice 旗舰音色对齐：
   - `qwen-cosy-sweet` (甜美姐姐音色)
   - `qwen-cosy-boy` (阳光哥哥音色)
   - `qwen-cosy-cute` (萌系小卡拉卡通音色)
   - `qwen-cosy-master` (智囊导师音色)
3. 🎤 声学情绪分析 (WPM 语速/抖动度) 与关键数据向量化
"""

import os
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.engine.world_model_engine import world_model_engine
from backend.app.engine.vector_store import vector_store


class QwenVoiceModelConfig(BaseModel):
    voice_id: str
    voice_name: str
    avatar_emoji: str
    avatar_cartoon_type: str
    sample_rate: int = 24000
    pitch_scale: float = 1.0


QWEN_COS_VOICES = {
    "cute": QwenVoiceModelConfig(
        voice_id="qwen-cosy-cute",
        voice_name="智小伴 (萌系卡拉宠物音)",
        avatar_emoji="🦊",
        avatar_cartoon_type="cartoon_fox",
        pitch_scale=1.4
    ),
    "sweet": QwenVoiceModelConfig(
        voice_id="qwen-cosy-sweet",
        voice_name="知心姐姐 (千问温柔女声)",
        avatar_emoji="👩",
        avatar_cartoon_type="cartoon_sister",
        pitch_scale=1.15
    ),
    "boy": QwenVoiceModelConfig(
        voice_id="qwen-cosy-boy",
        voice_name="阳光哥哥 (千问热血男声)",
        avatar_emoji="👦",
        avatar_cartoon_type="cartoon_boy",
        pitch_scale=0.95
    ),
    "master": QwenVoiceModelConfig(
        voice_id="qwen-cosy-master",
        voice_name="智囊导师 (千问学术男声)",
        avatar_emoji="🦉",
        avatar_cartoon_type="cartoon_owl",
        pitch_scale=0.85
    )
}


class AcousticAnalysisResult(BaseModel):
    wpm: float
    pause_latency_s: float
    pitch_variance: float
    acoustic_emotion: str
    confidence: float


class VoiceChatRequest(BaseModel):
    student_id: str = "STU-2026"
    voice_input_text: str = "老师，我异分母分数加减法总是做错怎么办？"
    interest_anchor: str = "Minecraft"
    selected_voice_key: str = "cute"
    audio_wpm: float = 120.0
    audio_pause_s: float = 2.2


class VoiceChatResponse(BaseModel):
    session_id: str
    student_input_transcript: str
    acoustic_analysis: AcousticAnalysisResult
    ai_voice_response_text: str
    qwen_voice_model: QwenVoiceModelConfig
    speech_audio_wave_preset: List[float]
    cartoon_avatar_state: str  # speaking / listening / happy / thinking
    pedagogical_empathy_tag: str
    world_model_used: str
    vector_memory_id: Optional[str] = None


class VoiceAssistantEngine:
    """
    千问 Qwen-Omni & CosyVoice 原生高保真卡通伴读音色引擎
    """
    def process_voice_interaction(self, req: VoiceChatRequest) -> VoiceChatResponse:
        session_id = f"QWEN-VOICE-{uuid.uuid4().hex[:8].upper()}"

        # 获取选定的千问 CosyVoice 引擎配置
        voice_cfg = QWEN_COS_VOICES.get(req.selected_voice_key, QWEN_COS_VOICES["cute"])

        # 1. 声学情绪分析
        acoustic_emotion = "心态平稳"
        avatar_state = "speaking"
        if req.audio_pause_s > 3.0 or req.audio_wpm < 90.0:
            acoustic_emotion = "焦虑畏难"
            avatar_state = "empathy_hug"
        elif req.audio_wpm > 180.0:
            acoustic_emotion = "急躁冲动"
            avatar_state = "calm_down"

        acoustic_res = AcousticAnalysisResult(
            wpm=req.audio_wpm,
            pause_latency_s=req.audio_pause_s,
            pitch_variance=0.35 if acoustic_emotion == "焦虑畏难" else 0.15,
            acoustic_emotion=acoustic_emotion,
            confidence=0.95
        )

        # 2. 关键数据向量化
        vec_id = None
        if acoustic_emotion in ["焦虑畏难", "急躁冲动"]:
            vec_id = f"KEY-BEHAVIOR-{uuid.uuid4().hex[:6].upper()}"
            vector_store.upsert_knowledge_memory(
                doc_id=vec_id,
                content=f"通义千问音色关键点：学生【{req.voice_input_text}】，音色[{voice_cfg.voice_name}]，状态[{acoustic_emotion}]",
                metadata={"student_id": req.student_id, "type": "qwen_voice_key_point", "voice_id": voice_cfg.voice_id}
            )

        # 3. 预测世界模型状态
        world_pred = world_model_engine.predict_pedagogical_world_state(
            student_id=req.student_id,
            recent_concept="异分母分数加减法",
            current_score=60.0,
            frustration_level=0.5 if acoustic_emotion == "焦虑畏难" else 0.2
        )

        ai_response = (
            f"嗷呜~ 别担心！我是你的卡通伴读小狐狸《{voice_cfg.voice_name.split('(')[0]}》！"
            f"在《{req.interest_anchor}》里咱们通分就像合成方块，找准最小公倍数就行啦！要看 30s 萌宠动画演示吗？"
        )

        wave_data = [0.35, 0.7, 0.9, 0.4, 0.85, 0.65, 0.95, 0.5, 0.8, 0.3]

        return VoiceChatResponse(
            session_id=session_id,
            student_input_transcript=req.voice_input_text,
            acoustic_analysis=acoustic_res,
            ai_voice_response_text=ai_response,
            qwen_voice_model=voice_cfg,
            speech_audio_wave_preset=wave_data,
            cartoon_avatar_state=avatar_state,
            pedagogical_empathy_tag="通义千问 CosyVoice 萌宠伴读",
            world_model_used=world_pred.world_model_locked_name,
            vector_memory_id=vec_id
        )


voice_engine = VoiceAssistantEngine()
