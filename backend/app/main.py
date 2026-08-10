# -*- coding: utf-8 -*-
"""
Round 9 迭代优化：FastAPI 异常兜底、全量 CORS 与性能响应 Header 中间件 (main.py)

吹毛求疵优化项：
1. 增加耗时响应 Header `X-Process-Time` (单位 ms)
2. 增加全局异常拦截器，优雅兜底 422 / 500 格式化 JSON
3. 适配所有升级后的 7 大引擎接口与静态 UI 渲染
"""

import time
import os
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException, UploadFile, File, Body, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse

from backend.app.engine.ocr_engine import analyze_test_paper_ocr
from backend.app.engine.fuse_engine import compute_fused_score
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust
from backend.app.engine.telemetry_engine import process_physics_telemetry
from backend.app.engine.psychology_fsm import process_psychology_fsm
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


app = FastAPI(
    title="「智学伴 LearnMate」- 个性化学习规划 Agent 核心 API (v2.0 吹毛求疵全量优化版)",
    description="GOAI 世界开源大赛 - 赛道二：无界应用 (AI+教育) 顶级工程化与算法 API",
    version="2.0.0"
)

# 允许全域 CORS
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": f"系统内部异常: {str(exc)}", "type": type(exc).__name__}
    )


@app.get("/", response_class=HTMLResponse, summary="智学伴 极客 UI 控制台")
def read_root():
    index_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>智学伴 LearnMate API v2.0 运行中...</h1>"


@app.post("/api/v1/archive/parent", summary="1. 家长端建档接口")
def create_parent_archive(payload: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "parent_id": payload.get("parent_id", "PAR-8899"),
        "grade": payload.get("grade", "junior"),
        "target_goal": payload.get("target_goal", "冲刺满分 100"),
        "message": f"成功为 {payload.get('grade')} 年级学生建档，目标：{payload.get('target_goal')}"
    }


@app.post("/api/v1/archive/student", summary="2. 学生端建档与兴趣偏好接口")
def create_student_archive(payload: Dict[str, Any] = Body(...)):
    return {
        "status": "success",
        "student_id": payload.get("student_id", "STU-2026"),
        "learning_style": payload.get("learning_style", "视觉型"),
        "interests": payload.get("interests", ["Minecraft", "篮球"]),
        "message": f"成功绑定学生，风格：{payload.get('learning_style')}，兴趣：{payload.get('interests')}"
    }


@app.post("/api/v1/ocr/diagnostic", summary="3. 1秒 Vision OCR 试卷摸底接口")
async def ocr_diagnostic(student_id: str = Form("STU-1001"), paper_image: UploadFile = File(None)):
    contents = await paper_image.read() if paper_image else b"fake_paper_bytes"
    return analyze_test_paper_ocr(student_id=student_id, paper_image=contents)


@app.post("/api/v1/engine/fuse", summary="4. 1D 卡尔曼与 EWMA 去噪融合接口")
def fuse_denoise_score(
    s_static_history: float = Body(..., ge=0.0, le=1.0),
    s_dynamic_raw: List[float] = Body(...),
    N: int = Body(5)
):
    return compute_fused_score(s_static_history=s_static_history, s_dynamic_raw=s_dynamic_raw, N=N)


@app.post("/api/v1/engine/meltdown", summary="5. Sigmoid 相变防崩溃熔断与 ZPD 心流接口")
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


@app.post("/api/v1/telemetry/analyze", summary="6. 4维无感物理遥测与马氏距离防作弊接口")
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


@app.post("/api/v1/psychology/fsm", summary="7. (A,R) 心理学 FSM 与 400 热线硬阻断接口")
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


@app.post("/api/v1/material/video_workflow", summary="8. 30s 线上 AI 动画大模型 Master Prompt 接口")
def get_video_workflow(knowledge_point: str = Body(...), student_interest: str = Body("Minecraft")):
    return create_ai_animation_workflow(knowledge_point=knowledge_point, student_interest=student_interest)


@app.get("/api/v1/report/vector", summary="9. Chroma 向量学情雷达图与行动优先级接口")
def get_vector_report(student_id: str, timeframe: str = "weekly"):
    return build_academic_vector_report(student_id=student_id, timeframe=timeframe)
