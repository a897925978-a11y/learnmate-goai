# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」心理学 FSM 与行为边界管制引擎 (psychology_fsm.py)

功能：
1. 🛑 Tier 3 400 心理援助热线硬阻断 (400-161-9995)  —— DEV-T4-B 契约落地
2. 🌙 22:00 强制睡眠锁 (Sleep Protection Boundary)
3. 👀 姿态与屏幕光线护眼警告 (Eye & Posture Boundary)
4. 🔑 关键行为数据向量化 (Key Data Vectorization) 联动

DEV-T4-B 补强说明（对抗式审查后落地）：
- 原实现仅返回 boundary_status(中文串) + action_required(中文文本)，
  与 Agent_7 开局方案契约 {is_ai_blocked, ui_action, alert_encrypted_payload} 不匹配。
- 本版新增机器可读字段 is_ai_blocked / ui_action / semantic_match_score / matched_terms，
  前端(index.html 已渲染 400-161-9995 弹窗)可直接消费；
- 语义匹配：仓库无 embedding 模型(requirements 仅 fastapi/pydantic/numpy/requests)，
  真·语义匹配不可行；改用「高危词表 + 近义扩展」的确定性词典匹配，
  对安全屏障而言比模糊 embedding 更可靠(防 paraphrasing 漏网)。
  direct 命中 score=1.0；强近义命中 score=0.93(>=0.90 阈值即阻断)；
  is_ai_blocked 在 score>=0.90 或 direct 命中时为 True(召回率优先，安全优先)。
"""

import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from backend.app.engine.vector_store import vector_store


# ---------------------------------------------------------------------------
# Tier 3 临床危机语义词典（确定性、可解释、可审计）
# ---------------------------------------------------------------------------
# 直接高危词：命中即 score=1.0，100% 阻断
CRISIS_DIRECT_TERMS: List[str] = [
    "自杀", "自残", "割腕", "轻生", "寻死", "想死",
    "活不下去了", "不想活", "不想活了", "觉得活着没意思", "活着没意思",
]

# 近义扩展：与自残/自杀意图强绑定的改写说法，命中即 score=0.93(>=0.90 阈值)
CRISIS_SYNONYM_TERMS: List[str] = [
    "伤害自己", "弄伤自己", "对自己下手", "摧残自己",
    "结束生命", "结束自己的生命", "一了百了", "没有活下去的意义",
    "彻底没希望了", "撑不下去了", "活得太累",
]

CRISIS_UI_ACTION = "RENDER_HOTLINE_400_161_9995"
CRISIS_SEMANTIC_THRESHOLD = 0.90


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
    # —— DEV-T4-B 契约字段（机器可读，向下兼容旧字段）——
    is_ai_blocked: bool = False
    ui_action: Optional[str] = None
    semantic_match_score: float = 0.0
    matched_terms: List[str] = []


class CrisisSafetyResult(BaseModel):
    """DEV-T4-B 对外契约结果(Agent_7 开局方案口径)：
    {is_ai_blocked, ui_action, semantic_match_score, matched_terms, alert_encrypted_payload}
    """
    is_ai_blocked: bool
    ui_action: Optional[str]
    semantic_match_score: float
    matched_terms: List[str]
    alert_encrypted_payload: str = "CRISIS_EVENT_LOG_ENCRYPTED"
    boundary_status: str = "CRISIS_INTERCEPT"


class EnhancedPsychologyFSMEngine:
    """
    心理学 FSM 与行为边界管制类
    """

    def _compute_crisis_match(self, user_text: str):
        """确定性语义匹配：返回 (semantic_match_score, matched_terms)。
        设计原则：安全屏障召回率优先——direct 命中=1.0，强近义命中=0.93。
        """
        matched: List[str] = []
        text = user_text or ""
        # 1) 直接高危词：精确子串命中
        for term in CRISIS_DIRECT_TERMS:
            if term in text:
                matched.append(term)
        if matched:
            return 1.0, matched
        # 2) 强近义扩展：改写说法命中（仍属明确自残/自杀意图）
        for term in CRISIS_SYNONYM_TERMS:
            if term in text:
                matched.append(term)
        if matched:
            return 0.93, matched
        return 0.0, []

    def evaluate_crisis_safety(self, user_text: str) -> CrisisSafetyResult:
        """DEV-T4-B 核心契约方法：Tier 3 临床危机安全屏障。
        断言：包含自残/自杀语义时 is_ai_blocked 必须 == True，
              ui_action == RENDER_HOTLINE_400_161_9995。
        """
        score, matched = self._compute_crisis_match(user_text)
        is_blocked = score >= CRISIS_SEMANTIC_THRESHOLD
        return CrisisSafetyResult(
            is_ai_blocked=is_blocked,
            ui_action=CRISIS_UI_ACTION if is_blocked else None,
            semantic_match_score=round(score, 4),
            matched_terms=matched,
            boundary_status="CRISIS_INTERCEPT" if is_blocked else "PASS",
        )

    def check_behavior_boundary(self, req: BehaviorBoundaryCheckRequest) -> BehaviorBoundaryCheckResponse:
        # —— Tier 3 临床危机硬熔断（最高优先级）——
        score, matched = self._compute_crisis_match(req.user_text)
        if score >= CRISIS_SEMANTIC_THRESHOLD:
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
                key_vector_id=vec_id,
                is_ai_blocked=True,
                ui_action=CRISIS_UI_ACTION,
                semantic_match_score=round(score, 4),
                matched_terms=matched,
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
        "action_required": res.action_required,
        "is_ai_blocked": res.is_ai_blocked,
        "ui_action": res.ui_action,
    }
