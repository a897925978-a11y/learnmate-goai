# -*- coding: utf-8 -*-
"""
模块 5：兴趣情境资料与线上 AI 动画生成大模型工作流引擎 (context_material.py)

功能：
1. 将枯燥的数学/科学知识点（如异分母分数加减法、勾股定理）映射到学生兴趣情境（如 Minecraft 建筑、原神伤害计算、篮球命中率）
2. 生成 30 秒线上 AI 视频/动画大模型 (Runway / Luma / CogVideo / 可灵) 的旁白脚本与 Prompt
"""

import uuid
from typing import Dict, Any, List
from backend.app.schemas.api_models import AIVideoWorkflowMetadata


class ContextualMaterialEngine:
    """
    兴趣情境化资料与 AI 动画工作流生成引擎
    """

    def generate_video_workflow(
        self,
        knowledge_point: str,
        student_interest: str = "Minecraft"
    ) -> AIVideoWorkflowMetadata:
        """
        生成 30 秒线上 AI 动画大模型生成脚本与 Prompts
        """
        video_id = f"VID-AI-{uuid.uuid4().hex[:8].upper()}"

        if "Minecraft" in student_interest or "游戏" in student_interest:
            context_desc = f"在《Minecraft》红石电路与方块建造中解析【{knowledge_point}】"
            script = (
                f"“嘿！在《Minecraft》里打造超级方块，如果方块分母不同，怎么合并力量？"
                f"别急！先把红石分母通分，化成分母相同的红石能量块，就能一键合成无限方块！”"
            )
            prompts = [
                f"3D Minecraft voxel style animation, showing redstone blocks combining, clear math explanation overlay of {knowledge_point}, 4k resolution",
                f"Cinematic educational animation, Minecraft character solving math puzzle with bright visual effects, bright lighting"
            ]
        else:
            context_desc = f"在日常篮球投篮命中率与运动轨迹中解析【{knowledge_point}】"
            script = (
                f"“想要在三分线外百发百中？这不仅靠手感，更靠数学公式！"
                f"把投篮抛物线拆解为通分分子，分母对齐后弧线精准落入篮筐！”"
            )
            prompts = [
                f"3D anime basketball shot trajectory animation, glowing math formula overlays of {knowledge_point}, dynamic camera movement, high quality",
                f"Vibrant educational video snippet, basketball player shooting with arc parabola calculation, clean aesthetic"
            ]

        return AIVideoWorkflowMetadata(
            video_id=video_id,
            knowledge_point=knowledge_point,
            interest_context=context_desc,
            audio_script=script,
            visual_prompts=prompts,
            duration_seconds=30
        )


def create_ai_animation_workflow(
    knowledge_point: str,
    student_interest: str = "Minecraft"
) -> AIVideoWorkflowMetadata:
    """
    对外调用的封装接口
    """
    engine = ContextualMaterialEngine()
    return engine.generate_video_workflow(knowledge_point=knowledge_point, student_interest=student_interest)
