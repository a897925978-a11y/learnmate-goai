# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」心理学 FSM 与行为边界管制引擎 (psychology_fsm.py)

功能：
1. 🛑 Tier 3 400 心理援助热线硬阻断 (400-161-9995)
2. 🌙 22:00 强制睡眠锁 (Sleep Protection Boundary)
3. 👀 姿态与屏幕光线护眼警告 (Eye & Posture Boundary)
4. 🔑 关键行为数据向量化 (Key Data Vectorization) 联动
"""

import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.engine.vector_store import vector_store


class BehaviorBoundaryCheckRequest(BaseModel):
    student_id: str = "STU-2026"
    current_hour: int = 20
    screen_distance_cm: float = 40.0
    ambient_light_lux: float = 300.0
    continuous_usage_minutes: int = 25
    user_text: str = "学习挺有意思"


class BehaviorBoundaryCheckResponse(BaseModel):
    boundary_status: str  # PASS / EYE_PROTECTION_WARN / SLEEP_LOCK_TRIGGERED / CRISIS_INTERCEPT
    message: str
    action_required: str
    key_vector_id: Optional[str] = None


class EnhancedPsychologyFSMEngine:
    """
    心理学 FSM 与行为边界管制类
    """
    def check_behavior_boundary(self, req: BehaviorBoundaryCheckRequest) -> BehaviorBoundaryCheckResponse:
        high_risk_words = ["自杀", "自残", "绝望", "活不下去了", "想死", "觉得活着没意思"]
        if any(w in req.user_text for w in high_risk_words):
            vec_id = f"CRISIS-KEY-{uuid.uuid4().hex[:6].upper()}"
            vector_store.upsert_knowledge_memory(
                doc_id=vec_id,
                content=f"高危心理预警关键点：触发死锁敏感词【{req.user_text}】，已被 400 热线防线截断",
                metadata={"student_id": req.student_id, "type": "crisis_key_point", "risk": "Tier3_High"}
            )
            return BehaviorBoundaryCheckResponse(
                boundary_status="CRISIS_INTERCEPT",
                message="🚨 心理安全防御系统拦截：识别到极度沮丧情绪，已自动阻断 AI 拟人化回答。",
                action_required="渲染 400-161-9995 国家心理援助热线弹窗并推送紧急提示给监护人",
                key_vector_id=vec_id
            )

        if req.current_hour >= 22 or req.current_hour < 6:
            return BehaviorBoundaryCheckResponse(
                boundary_status="SLEEP_LOCK_TRIGGERED",
                message="🌙 22:00 深夜睡眠保护触发：为了保证生长发育与第二天的学习精力，伴学系统已开启锁定。",
                action_required="强制弹出晚安动画屏，锁定主交互面板，鼓励按时就寝",
                key_vector_id=None
            )

        if req.screen_distance_cm < 30.0 or req.ambient_light_lux < 100.0 or req.continuous_usage_minutes > 45:
            vec_id = f"EYE-KEY-{uuid.uuid4().hex[:6].upper()}"
            vector_store.upsert_knowledge_memory(
                doc_id=vec_id,
                content=f"护眼边界点：视线距离{req.screen_distance_cm}cm, 环境光{req.ambient_light_lux}lux, 持续使用{req.continuous_usage_minutes}分钟",
                metadata={"student_id": req.student_id, "type": "posture_eye_key_point"}
            )
            return BehaviorBoundaryCheckResponse(
                boundary_status="EYE_PROTECTION_WARN",
                message="👀 姿态与屏幕护眼预警：眼睛距离屏幕过近或使用时间较长，请调整坐姿。",
                action_required="弹出护眼律动气泡，提示远眺放松",
                key_vector_id=vec_id
            )

        return BehaviorBoundaryCheckResponse(
            boundary_status="PASS",
            message="✅ 行为与环境边界符合健康标准",
            action_required="继续陪伴交互",
            key_vector_id=None
        )


PsychologyFSMEngine = EnhancedPsychologyFSMEngine
psychology_fsm_engine = EnhancedPsychologyFSMEngine()


def process_psychology_fsm(user_input_text: str, parent_target: str = "100", student_actual: float = 65.0, current_hour: int = 20):
    req = BehaviorBoundaryCheckRequest(
        user_text=user_input_text,
        current_hour=current_hour
    )
    res = psychology_fsm_engine.check_behavior_boundary(req)
    return {
        "status": "COMPLETED",
        "current_state": res.boundary_status,
        "adlerian_guidance": res.message,
        "action_required": res.action_required
    }
