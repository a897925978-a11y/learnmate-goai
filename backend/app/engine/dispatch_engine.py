# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」教育端 (家长/教师) 与被教育端 (学生) 现象级推送与人工干预调度引擎 (dispatch_engine.py)

合规铁律 (Non-Diagnostic Regulatory Guardrail)：
1. 绝对禁止输出任何心理学诊断标签或评语（如“焦虑症”、“心理不健康”等违规评价）；
2. 仅客观陈述观测到的物理现象与行为事实（如“连续停顿 4 分钟”、“删除率提升”）；
3. 自动将客观现象推送至【家长端】与【教师端】，引导人工干预陪伴。
"""

import datetime
import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class ObjectivePhenomenonAlert(BaseModel):
    alert_id: str
    student_id: str
    event_timestamp: str
    target_roles: List[str] = Field(default_factory=lambda: ["Parent", "Teacher"])
    observed_phenomena: List[str] = Field(..., description="纯客观行为与环境观测现象（严禁任何心理学诊断评价）")
    suggested_human_action: str = Field(..., description="建议的人工干预动作")
    compliance_non_diagnostic_flag: bool = Field(True, description="合规性标识：纯现象陈述，无诊断结论")


class DualRoleDispatchEngine:
    """
    双端现象级推送调度类
    """
    def __init__(self):
        self.dispatched_alerts: List[ObjectivePhenomenonAlert] = []

    def evaluate_and_dispatch(
        self,
        student_id: str,
        pause_duration_s: float,
        backspace_rate: float,
        user_input_text: str,
        screen_distance_cm: float,
        current_hour: int
    ) -> Optional[ObjectivePhenomenonAlert]:
        phenomena = []
        action = "进行温和陪伴与针对性解题指导"

        # 1. 监测连续卡顿现象
        if pause_duration_s > 180.0:
            phenomena.append(f"观测现象：在当前题目上连续静置/停顿超过 {int(pause_duration_s // 60)} 分钟未作答")

        # 2. 监测按键频繁删除现象
        if backspace_rate > 8.0:
            phenomena.append(f"观测现象：答题框按键删除率为 {backspace_rate:.1f} 次/分钟，出现多次重复尝试与涂改")

        # 3. 监测屏幕距离现象
        if screen_distance_cm < 25.0:
            phenomena.append(f"观测现象：头部视线距离屏幕为 {screen_distance_cm} cm (推荐大于 35 cm)")
            action = "提醒孩子调整坐姿并休息眼睛"

        # 4. 监测深夜作息现象
        if current_hour >= 21:
            phenomena.append(f"观测现象：学习时间已到达晚间 {current_hour}:00 点，已连续学习较长时间")
            action = "建议准备准备整理书包并按时休息"

        # 若未触发明显异样现象，不滥发推送
        if not phenomena:
            return None

        alert = ObjectivePhenomenonAlert(
            alert_id=f"DISPATCH-{uuid.uuid4().hex[:8].upper()}",
            student_id=student_id,
            event_timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            target_roles=["Parent", "Teacher"],
            observed_phenomena=phenomena,
            suggested_human_action=action,
            compliance_non_diagnostic_flag=True
        )

        self.dispatched_alerts.append(alert)
        return alert

    def get_parent_teacher_alerts(self, student_id: str) -> List[ObjectivePhenomenonAlert]:
        return [a for a in self.dispatched_alerts if a.student_id == student_id]


dispatch_engine = DualRoleDispatchEngine()
