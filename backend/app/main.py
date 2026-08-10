# -*- coding: utf-8 -*-
"""
统一 FastAPI 主路由控制层 (main.py) - v5.0 已锁定 Qwen3.5-Omni 世界模型与智能语音上线
"""

import time
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.engine.profiling_engine import (
    profiling_engine,
    StudentIdentityRecord,
    MedicalCheckupRecord,
    StudentDiaryJournalRecord
)

from backend.app.engine.world_model_engine import world_model_engine
from backend.app.engine.voice_engine import voice_engine, VoiceChatRequest
from backend.app.engine.textin_ocr import textin_engine

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.psychology_fsm import process_psychology_fsm
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 锁定 Qwen3.5-Omni 世界模型与全双工智能语音 Agent",
    description="GOAI 开源大赛 - 锁定世界模型算控，上线智能语音交互",
    version="5.0.0"
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
    return "<h1>智学伴 LearnMate 世界模型与语音 Agent 服务运行中...</h1>"


# ----------------------------------------------------------------------
# 🌍 锁定世界模型 & 🎙️ 智能语音助手 RESTful APIs
# ----------------------------------------------------------------------

@app.post("/api/v1/world/predict", summary="锁定 Qwen3.5-Omni 世界模型：预测认知状态转移")
def predict_world_state(
    student_id: str = Body("STU-2026"),
    recent_concept: str = Body("异分母分数加减法"),
    current_score: float = Body(60.0),
    frustration_level: float = Body(0.4)
):
    pred = world_model_engine.predict_pedagogical_world_state(
        student_id=student_id,
        recent_concept=recent_concept,
        current_score=current_score,
        frustration_level=frustration_level
    )
    return pred.model_dump()


@app.post("/api/v1/voice/chat", summary="上线智能语音助手：接收语音/文本，合成全双工伴学回答")
def voice_assistant_chat(req: VoiceChatRequest):
    res = voice_engine.process_voice_interaction(req)
    return res.model_dump()


# ----------------------------------------------------------------------
# 全闭环与底层引擎 APIs
# ----------------------------------------------------------------------

@app.post("/api/v1/omni/student_lifecycle_ingest", summary="全维吸收: 入库学生学籍、体检报告、日记随笔与全维档案")
def ingest_student_lifecycle(
    identity: StudentIdentityRecord,
    health_checkup: Optional[MedicalCheckupRecord] = None,
    diary_entry: Optional[StudentDiaryJournalRecord] = None,
    interests: List[str] = Body(["Minecraft", "篮球"]),
    anxiety_score: int = Body(3)
):
    profile = profiling_engine.ingest_full_student_data(
        identity=identity,
        health_checkup=health_checkup,
        diary_entry=diary_entry,
        interests=interests,
        anxiety_score=anxiety_score
    )
    return profile.model_dump()


@app.post("/api/v1/ocr/diagnostic", summary="Vision OCR 摸底接口")
async def ocr_diagnostic(student_id: str = Form("STU-2026"), paper_image: Optional[UploadFile] = File(None)):
    contents = await paper_image.read() if paper_image else b"fake_bytes"
    return analyze_test_paper_ocr(student_id=student_id, paper_image=contents)


@app.post("/api/v1/psychology/fsm", summary="(A,R) 心理学 FSM 与 400 热线硬阻断")
def evaluate_psychology_fsm(user_input_text: str = Body("数学怎么学"), parent_target: str = Body("冲刺满分"), student_actual: float = Body(0.65), current_hour: int = Body(20)):
    return process_psychology_fsm(user_input_text=user_input_text, parent_target=parent_target, student_actual=student_actual, current_hour=current_hour)


@app.get("/api/v1/report/vector", summary="Chroma 向量学情雷达图")
def get_vector_report(student_id: str = "STU-2026", timeframe: str = "weekly"):
    return build_academic_vector_report(student_id=student_id, timeframe=timeframe)
