# -*- coding: utf-8 -*-
"""
统一 FastAPI 主路由控制层 (main.py)
包含【任务包 1：双端初始建档与 Vision OCR 摸底模块】及全套 API 路由
"""

import time
import os
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.engine.profiling_engine import (
    profiling_engine,
    ParentProfileRequest,
    StudentPsychologyInterestRequest,
    QuizAnswerItem
)

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.psychology_fsm import process_psychology_fsm
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 任务包 1 双端初始建档与 Vision OCR 摸底服务",
    description="GOAI 世界开源大赛 - 赛道二：无界应用 (AI+教育) 任务包 1 规格契约服务",
    version="3.0.0"
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
    return "<h1>智学伴 LearnMate 任务包 1 服务运行中...</h1>"


# ----------------------------------------------------------------------
# 任务包 1 核心 API 契约路由
# ----------------------------------------------------------------------

@app.post("/api/v1/task1/parent_profile", summary="任务包1: 家长端学籍/教材/目标/标签建档 API")
def task1_parent_profile(req: ParentProfileRequest):
    res = profiling_engine.create_parent_profile(req)
    return res.model_dump()


@app.post("/api/v1/task1/student_psychology_interest", summary="任务包1: 3-5题学习风格/焦虑度/兴趣建档 API")
def task1_student_psychology_interest(req: StudentPsychologyInterestRequest):
    res = profiling_engine.evaluate_student_psychology_interest(req)
    return res.model_dump()


@app.post("/api/v1/task1/vision_ocr_diagnostic", summary="任务包1: 试卷拍照上传 Vision OCR 解析错因归因 API")
async def task1_vision_ocr_diagnostic(student_id: str = Form("STU-2026"), paper_image: Optional[UploadFile] = File(None)):
    contents = await paper_image.read() if paper_image else None
    res = profiling_engine.process_vision_ocr_diagnostic(student_id=student_id, image_bytes=contents)
    return res.model_dump()


# ----------------------------------------------------------------------
# 其他辅助引擎 API
# ----------------------------------------------------------------------

@app.post("/api/v1/archive/parent", summary="家长端建档兜底接口")
def create_parent_archive(payload: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "parent_id": payload.get("parent_id", "PAR-8899"),
        "grade": payload.get("grade", "初二"),
        "message": "家长档案更新成功"
    }


@app.post("/api/v1/archive/student", summary="学生端建档兜底接口")
def create_student_archive(payload: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "student_id": payload.get("student_id", "STU-2026"),
        "message": "学生档案更新成功"
    }


@app.post("/api/v1/ocr/diagnostic", summary="Vision OCR 摸底兜底接口")
async def ocr_diagnostic(student_id: str = Form("STU-1001"), paper_image: Optional[UploadFile] = File(None)):
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
