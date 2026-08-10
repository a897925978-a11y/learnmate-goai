# -*- coding: utf-8 -*-
"""
统一 FastAPI 主路由控制层 (main.py) - 包含全场景教育闭环全维学生档案 API
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

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.psychology_fsm import process_psychology_fsm
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 全场景教育闭环全维学生档案 Agent 服务",
    description="GOAI 开源大赛 - 吸收全维度学生数据 (体检报告、学籍身份、日记随笔、试卷摸底)",
    version="4.0.0"
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
    return "<h1>智学伴 LearnMate 全闭环教育服务运行中...</h1>"


# ----------------------------------------------------------------------
# 🌟 全场景教育闭环全维学生档案 RESTful API 接口
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


@app.post("/api/v1/omni/add_health_checkup", summary="吸收单条医疗体检报告 (视力/BMI/睡眠/运动)")
def add_health_checkup(student_id: str = Body(...), checkup: MedicalCheckupRecord = Body(...)):
    return profiling_engine.add_health_checkup(student_id=student_id, checkup=checkup)


@app.post("/api/v1/omni/add_diary_journal", summary="吸收单条学生日记/成长随笔 (包含 AI 情绪识别)")
def add_diary_journal(student_id: str = Body(...), diary: StudentDiaryJournalRecord = Body(...)):
    return profiling_engine.add_diary_entry(student_id=student_id, entry=diary)


# ----------------------------------------------------------------------
# 辅助与遗留引擎 API 接口
# ----------------------------------------------------------------------

@app.post("/api/v1/ocr/diagnostic", summary="Vision OCR 摸底接口")
async def ocr_diagnostic(student_id: str = Form("STU-2026"), paper_image: Optional[UploadFile] = File(None)):
    contents = await paper_image.read() if paper_image else b"fake_bytes"
    return analyze_test_paper_ocr(student_id=student_id, paper_image=contents)


@app.post("/api/v1/engine/fuse", summary="卡尔曼与 EWMA 去噪融合")
def fuse_denoise_score(s_static_history: float = Body(0.5), s_dynamic_raw: List[float] = Body([0.2, 0.8]), N: int = Body(5)):
    return compute_fused_score(s_static_history=s_static_history, s_dynamic_raw=s_dynamic_raw, N=N)


@app.post("/api/v1/engine/meltdown", summary="Sigmoid 相变防崩溃熔断")
def evaluate_meltdown(consecutive_errors: int = Body(4), frustration_level: float = Body(0.85), current_difficulty: float = Body(0.85)):
    return check_meltdown_and_adjust(consecutive_errors=consecutive_errors, frustration_level=frustration_level, current_difficulty=current_difficulty)


@app.post("/api/v1/telemetry/analyze", summary="4维无感物理遥测")
def analyze_telemetry(user_declared_state: str = Body("完全懂了"), first_key_latency_ms: float = Body(3200.0), backspace_rate: float = Body(9.0), option_hover_ms: float = Body(1600.0), submission_duration_s: float = Body(30.0)):
    return process_physics_telemetry(user_declared_state=user_declared_state, first_key_latency_ms=first_key_latency_ms, backspace_rate=backspace_rate, option_hover_ms=option_hover_ms, submission_duration_s=submission_duration_s)


@app.post("/api/v1/psychology/fsm", summary="(A,R) 心理学 FSM 与 400 热线硬阻断")
def evaluate_psychology_fsm(user_input_text: str = Body("数学怎么学"), parent_target: str = Body("冲刺满分"), student_actual: float = Body(0.65), current_hour: int = Body(20)):
    return process_psychology_fsm(user_input_text=user_input_text, parent_target=parent_target, student_actual=student_actual, current_hour=current_hour)


@app.post("/api/v1/material/video_workflow", summary="30s 线上 AI 动画 Master Prompt")
def get_video_workflow(knowledge_point: str = Body("异分母分数加减法"), student_interest: str = Body("Minecraft")):
    return create_ai_animation_workflow(knowledge_point=knowledge_point, student_interest=student_interest)


@app.get("/api/v1/report/vector", summary="Chroma 向量学情雷达图")
def get_vector_report(student_id: str = "STU-2026", timeframe: str = "weekly"):
    return build_academic_vector_report(student_id=student_id, timeframe=timeframe)
