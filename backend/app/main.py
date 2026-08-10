# -*- coding: utf-8 -*-
"""
模块 7：统一 FastAPI 主路由控制层与双端 RESTful API 交互服务器 (main.py)

功能：
整合 1-6 所有核心引擎模块，对外提供标准的 RESTful 接口：
1. POST /api/v1/archive/parent - 家长端建档
2. POST /api/v1/archive/student - 学生端建档
3. POST /api/v1/ocr/diagnostic - 1秒 Vision OCR 试卷摸底
4. POST /api/v1/engine/fuse - 1D 卡尔曼与 EWMA 去噪融合
5. POST /api/v1/engine/meltdown - Sigmoid 相变防崩溃熔断判定
6. POST /api/v1/telemetry/analyze - 4维无感物理遥测与防装懂装累
7. POST /api/v1/psychology/fsm - (A,R) 心理学 FSM 与 400 热线硬阻断
8. POST /api/v1/material/video_workflow - 30s 线上 AI 动画大模型工作流
9. GET  /api/v1/report/vector - Chroma 向量多阶雷达图诊断报告
"""

from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Body
from fastapi.middleware.cors import CORSMiddleware

from backend.app.schemas.api_models import (
    ParentArchiveRequest, StudentArchiveRequest, OCRDiagnosticResponse,
    DailyCheckinRequest, PrivacyShieldResponse, AIVideoWorkflowMetadata,
    MultiScaleReportResponse, VectorReportTimeframe
)

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.psychology_fsm import process_psychology_fsm
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 个性化学习规划 Agent 核心引擎 API",
    description="GOAI 世界人工智能开源大赛 - 赛道二：无界应用 (AI+教育) 后端核心算控 API",
    version="1.0.0"
)

# 允许跨域 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": "智学伴 LearnMate Agent Core API",
        "competition": "GOAI Open Source Competition - Track 2 (AI+Education)"
    }


@app.post("/api/v1/archive/parent", summary="家长端建档与目标设定")
def create_parent_archive(req: ParentArchiveRequest):
    return {
        "status": "success",
        "parent_id": req.parent_id,
        "message": f"成功为 {req.grade.value} 年级学生建档，目标：{req.target_goal}"
    }


@app.post("/api/v1/archive/student", summary="学生端建档与兴趣心理偏好")
def create_student_archive(req: StudentArchiveRequest):
    return {
        "status": "success",
        "student_id": req.student_id,
        "message": f"成功绑定学生，学习风格：{req.learning_style}，兴趣偏好：{req.interests}"
    }


@app.post("/api/v1/ocr/diagnostic", response_model=OCRDiagnosticResponse, summary="1秒 Vision OCR 试卷错题摸底")
async def ocr_diagnostic(student_id: str = Body(...), paper_image: UploadFile = File(None)):
    contents = await paper_image.read() if paper_image else b"fake_image_content"
    return analyze_test_paper_ocr(student_id=student_id, paper_image=contents)


@app.post("/api/v1/engine/fuse", summary="1D 卡尔曼滤波 + EWMA 去噪融合算法")
def fuse_denoise_score(
    s_static_history: float = Body(..., ge=0.0, le=1.0),
    s_dynamic_raw: List[float] = Body(...),
    N: int = Body(5)
):
    return compute_fused_score(s_static_history=s_static_history, s_dynamic_raw=s_dynamic_raw, N=N)


@app.post("/api/v1/engine/meltdown", summary="Sigmoid 相变防崩溃熔断判定")
def evaluate_meltdown(
    consecutive_errors: int = Body(..., ge=0),
    frustration_level: float = Body(..., ge=0.0, le=1.0),
    current_difficulty: float = Body(0.8, ge=0.0, le=1.0)
):
    return check_meltdown_and_adjust(
        consecutive_errors=consecutive_errors,
        frustration_level=frustration_level,
        current_difficulty=current_difficulty
    )


@app.post("/api/v1/telemetry/analyze", summary="4维无感物理遥测与防装懂装累判定")
def analyze_telemetry(
    user_declared_state: str = Body(...),
    first_key_latency_ms: float = Body(...),
    backspace_rate: float = Body(...),
    option_hover_ms: float = Body(...),
    submission_duration_s: float = Body(...)
):
    return process_physics_telemetry(
        user_declared_state=user_declared_state,
        first_key_latency_ms=first_key_latency_ms,
        backspace_rate=backspace_rate,
        option_hover_ms=option_hover_ms,
        submission_duration_s=submission_duration_s
    )


@app.post("/api/v1/psychology/fsm", summary="(A,R) 心理学 FSM 与 400 热线硬阻断")
def evaluate_psychology_fsm(
    user_input_text: str = Body(...),
    parent_target: str = Body("冲刺满分"),
    student_actual: float = Body(0.65),
    current_hour: int = Body(20)
):
    return process_psychology_fsm(
        user_input_text=user_input_text,
        parent_target=parent_target,
        student_actual=student_actual,
        current_hour=current_hour
    )


@app.post("/api/v1/material/video_workflow", response_model=AIVideoWorkflowMetadata, summary="30s 线上 AI 动画大模型工作流")
def get_video_workflow(knowledge_point: str = Body(...), student_interest: str = Body("Minecraft")):
    return create_ai_animation_workflow(knowledge_point=knowledge_point, student_interest=student_interest)


@app.get("/api/v1/report/vector", response_model=MultiScaleReportResponse, summary="Chroma 向量学情诊断多阶雷达图")
def get_vector_report(student_id: str, timeframe: VectorReportTimeframe = VectorReportTimeframe.WEEKLY):
    return build_academic_vector_report(student_id=student_id, timeframe=timeframe)
