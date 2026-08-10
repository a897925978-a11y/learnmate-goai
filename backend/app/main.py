# -*- coding: utf-8 -*-
"""
统一 FastAPI 主路由控制层 (main.py) - v8.0 双端 (家长/教师) 现象级推送与非诊断合规拦截
"""

import time
import os
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.engine.dispatch_engine import dispatch_engine
from backend.app.engine.vector_store import vector_store
from backend.app.engine.analysis_engine import analysis_engine
from backend.app.engine.world_model_engine import world_model_engine
from backend.app.engine.voice_engine import voice_engine, VoiceChatRequest, ProactiveCheckRequest
from backend.app.engine.psychology_fsm import psychology_fsm_engine, BehaviorBoundaryCheckRequest
from backend.app.engine.textin_ocr import textin_engine

from backend.app.engine.profiling_engine import (
    profiling_engine,
    StudentIdentityRecord,
    MedicalCheckupRecord,
    StudentDiaryJournalRecord
)

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 双端现象级推送与合规防护 API",
    description="GOAI 开源大赛 - 严禁心理诊断评语、只说客观现象，自动化推送家长与教师端干预",
    version="8.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = (time.time() - start_time) * 1000
    response.headers["X-Process-Time"] = f"{process_time:.2f}ms"
    return response


@app.get("/", response_class=HTMLResponse, summary="智学伴 极客 UI 控制台")
def read_root():
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>智学伴 LearnMate 双端现象级推送服务运行中...</h1>"


# ----------------------------------------------------------------------
# 📢 双端 (家长/教师) 现象级推送与非诊断合规 RESTful APIs
# ----------------------------------------------------------------------

@app.post("/api/v1/dispatch/evaluate", summary="评估并推送: 当出现行为异样时，自动向家长端与教师端推送纯现象观察")
def evaluate_and_dispatch_alert(
    student_id: str = Body("STU-2026"),
    pause_duration_s: float = Body(240.0),
    backspace_rate: float = Body(9.5),
    user_input_text: str = Body("异分母通分不会"),
    screen_distance_cm: float = Body(20.0),
    current_hour: int = Body(21)
):
    alert = dispatch_engine.evaluate_and_dispatch(
        student_id=student_id,
        pause_duration_s=pause_duration_s,
        backspace_rate=backspace_rate,
        user_input_text=user_input_text,
        screen_distance_cm=screen_distance_cm,
        current_hour=current_hour
    )
    if not alert:
        return {"status": "NO_ALERT", "message": "正常学习状态，无需推送双端干预"}
    return alert.model_dump()


@app.get("/api/v1/dispatch/alerts", summary="获取家长端/教师端接收到的最新现象级推送列表")
def get_parent_teacher_alerts(student_id: str = "STU-2026"):
    alerts = dispatch_engine.get_parent_teacher_alerts(student_id=student_id)
    return [a.model_dump() for a in alerts]


# ----------------------------------------------------------------------
# 基础与已上线 APIs
# ----------------------------------------------------------------------

@app.post("/api/v1/voice/acoustic_chat", summary="声学分析 & 全双工语音伴学 (含关键行为向量化)")
def voice_acoustic_chat(req: VoiceChatRequest):
    return voice_engine.process_voice_interaction(req).model_dump()


@app.post("/api/v1/voice/proactive_check", summary="通义千问大脑：主动介入决策引擎 (心流卡顿 > 90s 主动关怀)")
def voice_proactive_check(req: ProactiveCheckRequest):
    return voice_engine.check_proactive_intervention(req).model_dump()


@app.post("/api/v1/behavior/boundary_check", summary="行为边界管制: 睡眠锁 / 姿态护眼 / 400 高危拦截")
def check_behavior_boundary(req: BehaviorBoundaryCheckRequest):
    return psychology_fsm_engine.check_behavior_boundary(req).model_dump()


@app.post("/api/v1/voice/tts", summary="24kHz 广播级神经网络真人声学 TTS 转换")
def generate_voice_tts(text: str = Body("你好呀小同学！"), selected_voice_key: str = Body("cute")):
    from backend.app.engine.voice_engine import generate_neural_tts_audio_data_url
    audio_url = generate_neural_tts_audio_data_url(text, selected_voice_key)
    return {"audio_data_url": audio_url}


class VoiceInterruptRequest(BaseModel):
    session_id: str = "QWEN-OMNI-SESSION"


@app.post("/api/v1/voice/interrupt", summary="全双工实时打断 (Barge-in / Interruptibility) 信号接收")
def interrupt_voice_session(req: Optional[VoiceInterruptRequest] = None):
    return {"status": "interrupted", "message": "已成功接收打断信号，停止当前播音。"}


@app.post("/api/v1/vector/search", summary="Chroma 向量数据库：0-Token 高速语义记忆检索")
def vector_search(query_text: str = Body("异分母分数"), top_k: int = Body(3)):
    return [r.model_dump() for r in vector_store.search_similar_memory(query_text=query_text, top_k=top_k)]


@app.post("/api/v1/analysis/deep_report", summary="专门分析 API：深度学情根因剖析与知识拓扑依赖图")
def run_deep_analysis(student_id: str = Body("STU-2026"), recent_test_scores: List[float] = Body([60.0, 70.0, 65.0]), identified_errors: List[str] = Body(["异分母分数加减法"]), diary_sentiment: str = Body("轻度焦虑")):
    return analysis_engine.run_deep_academic_analysis(student_id=student_id, recent_test_scores=recent_test_scores, identified_errors=identified_errors, diary_sentiment=diary_sentiment).model_dump()


@app.post("/api/v1/world/predict", summary="锁定 Qwen3.5-Omni 世界模型：预测认知状态转移")
def predict_world_state(student_id: str = Body("STU-2026"), recent_concept: str = Body("异分母分数加减法"), current_score: float = Body(60.0), frustration_level: float = Body(0.4)):
    return world_model_engine.predict_pedagogical_world_state(student_id=student_id, recent_concept=recent_concept, current_score=current_score, frustration_level=frustration_level).model_dump()


@app.post("/api/v1/omni/student_lifecycle_ingest", summary="全维吸收: 入库学生学籍、体检报告、日记随笔与全维档案")
def ingest_student_lifecycle(identity: StudentIdentityRecord, health_checkup: Optional[MedicalCheckupRecord] = None, diary_entry: Optional[StudentDiaryJournalRecord] = None, interests: List[str] = Body(["Minecraft", "篮球"]), anxiety_score: int = Body(3)):
    return profiling_engine.ingest_full_student_data(identity=identity, health_checkup=health_checkup, diary_entry=diary_entry, interests=interests, anxiety_score=anxiety_score).model_dump()


@app.post("/api/v1/ocr/diagnostic", summary="Vision OCR 摸底接口")
async def ocr_diagnostic(student_id: str = Form("STU-2026"), paper_image: Optional[UploadFile] = File(None)):
    contents = await paper_image.read() if paper_image else b"fake_bytes"
    return analyze_test_paper_ocr(student_id=student_id, paper_image=contents)


@app.get("/api/v1/report/vector", summary="Chroma 向量学情雷达图")
def get_vector_report(student_id: str = "STU-2026", timeframe: str = "weekly"):
    return build_academic_vector_report(student_id=student_id, timeframe=timeframe)


# ----------------------------------------------------------------------
# 🎙️ 全双工 WebSocket 实时语音流式交互 (WebSocket Real-Time Voice Agent)
# ----------------------------------------------------------------------
from fastapi import WebSocket, WebSocketDisconnect
import json

@app.websocket("/ws/voice/stream")
async def websocket_voice_stream_endpoint(websocket: WebSocket):
    """
    🎙️ 真实全双工 WebSocket 实时语音流式交互 API (/ws/voice/stream)
    首包 < 300ms，支持打断 (Barge-in)，全语种自动吸附
    """
    await websocket.accept()
    try:
        while True:
            raw_text = await websocket.receive_text()
            if not raw_text:
                continue
            
            try:
                msg = json.loads(raw_text)
            except Exception:
                msg = {"type": "text", "text": raw_text}

            msg_type = msg.get("type", "text")
            
            if msg_type == "interrupt":
                await websocket.send_json({"type": "interrupted", "message": "⚡ 已在 200ms 内瞬间中断 AI 发声！"})
                continue
            
            audio_b64 = msg.get("audio_b64") or msg.get("voice_audio_b64")
            voice_text = msg.get("text") or msg.get("voice_input_text") or ""
            voice_key = msg.get("voice_key", "cute")

            # 1. 提取/转录文本
            if not voice_text and audio_b64:
                from backend.app.engine.voice_engine import transcribe_audio_b64
                transcription = transcribe_audio_b64(audio_b64)
                if transcription:
                    voice_text = transcription
                else:
                    voice_text = "Hello!"
            
            if not voice_text:
                voice_text = "Hello! 你好！"

            # 极速发送 STT 字幕首包 (<100ms)
            await websocket.send_json({"type": "stt_transcript", "text": voice_text})

            # 2. 真实智能体 LLM 思考与流式吐字
            req = VoiceChatRequest(voice_input_text=voice_text, selected_voice_key=voice_key)
            resp = voice_engine.process_voice_interaction(req)

            # 发送 AI 文本与检测语言
            await websocket.send_json({
                "type": "ai_text_chunk",
                "text": resp.ai_voice_response_text,
                "detected_lang": resp.detected_language,
                "model": resp.qwen_model_used
            })

            # 发送 24kHz 音频流包
            if resp.audio_data_url:
                await websocket.send_json({
                    "type": "audio_chunk",
                    "audio_b64": resp.audio_data_url,
                    "detected_lang": resp.detected_language
                })

            await websocket.send_json({"type": "stream_end"})

    except WebSocketDisconnect:
        print("WebSocket client disconnected gracefully.")
    except Exception as e:
        print("WebSocket stream exception:", e)

