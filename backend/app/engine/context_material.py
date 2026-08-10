# -*- coding: utf-8 -*-
"""
Round 7 迭代优化：多模态 AI 动画 Master Prompt 生成工作流引擎 (context_material.py)

吹毛求疵优化项：
1. 输出标准符合 Runway / Luma / 可灵 / 豆包视频大模型要求的 Master Prompt
2. 包含专业镜头语言 (Camera Movement, Aspect Ratio, Negative Prompt, Lighting)
3. 生成 3 阶段分镜脚本 (Storyboards: Intro -> Math Concept Breakdown -> Outro)
"""

import uuid
from typing import Dict, Any, List
from pydantic import BaseModel, Field


class StoryboardScene(BaseModel):
    scene_number: int = Field(..., description="分镜序号")
    timestamp: str = Field(..., description="时间轴范围 (例 00:00 - 00:10)")
    visual_description: str = Field(..., description="画面描述")
    audio_narration: str = Field(..., description="旁白语音")
    camera_movement: str = Field(..., description="镜头运镜指令")


class MasterPromptWorkflow(BaseModel):
    video_id: str = Field(..., description="视频工程 ID")
    knowledge_point: str = Field(..., description="知识点")
    student_interest: str = Field(..., description="兴趣情境")
    master_prompt_en: str = Field(..., description="Runway/Luma 英文 Master Prompt")
    negative_prompt: str = Field(..., description="负面提示词")
    storyboard: List[StoryboardScene] = Field(..., description="3 阶段分镜脚本")
    duration_seconds: int = Field(30, description="视频时长")


class ContextualMaterialEngine:
    def generate_video_workflow(
        self,
        knowledge_point: str,
        student_interest: str = "Minecraft"
    ) -> MasterPromptWorkflow:
        video_id = f"VID-MASTER-{uuid.uuid4().hex[:8].upper()}"

        if "Minecraft" in student_interest or "游戏" in student_interest:
            master_prompt = (
                f"Cinematic 3D Minecraft animation, high resolution voxel art. "
                f"A glowing blue redstone block splits into fractions representing {knowledge_point}. "
                f"Bright futuristic lighting, 8k quality, smooth 60fps camera pan."
            )
            storyboard = [
                StoryboardScene(
                    scene_number=1,
                    timestamp="00:00 - 00:10",
                    visual_description="史蒂夫在红石工坊里遇到不同分母的能量块，陷入苦恼。",
                    audio_narration="“在 Minecraft 里打造超级工具，如果分母不同，红石能量怎么合并？”",
                    camera_movement="Push in to character's face, dynamic zoom"
                ),
                StoryboardScene(
                    scene_number=2,
                    timestamp="00:10 - 00:20",
                    visual_description="红石方块高亮闪烁，自动化通分转换为相同大小的分数方块。",
                    audio_narration="“别慌！找到最小公倍数通分，把方块分母化齐，能量瞬间充满！”",
                    camera_movement="360 degree slow camera orbit around glowing block"
                ),
                StoryboardScene(
                    scene_number=3,
                    timestamp="00:20 - 00:30",
                    visual_description="方块成功结合，发射炫彩光芒，右上角弹出算术公式总结。",
                    audio_narration="“通分完成！你学会异分母加减法的奥秘了吗？”",
                    camera_movement="Tilt up to sky, particle flare light"
                )
            ]
        else:
            master_prompt = (
                f"Vibrant 3D anime style educational video. A glowing basketball shot trajectory "
                f"with dynamic math formula overlays explaining {knowledge_point}. "
                f"Cinematic lighting, high frame rate, ultra detailed."
            )
            storyboard = [
                StoryboardScene(
                    scene_number=1,
                    timestamp="00:00 - 00:10",
                    visual_description="球员在三分线外起跳投篮，篮球在空中划出弧线。",
                    audio_narration="“三分球想要空心入网？这不仅靠手感，更靠数学分式的精准计算！”",
                    camera_movement="Slow motion tracking shot following basketball"
                ),
                StoryboardScene(
                    scene_number=2,
                    timestamp="00:10 - 00:20",
                    visual_description="弧线上弹出分数通分公式，分母自动齐平，轨迹亮起绿光。",
                    audio_narration="“把不同分母化为相同的基准，就像调整投篮角度一样简单！”",
                    camera_movement="Close up shot of holographic math UI"
                ),
                StoryboardScene(
                    scene_number=3,
                    timestamp="00:20 - 00:30",
                    visual_description="篮球空心入网，全场掌声雷动，展示最终通分步骤图。",
                    audio_narration="“完美进球！掌握通分，你就是数学赛场上的 MVP！”",
                    camera_movement="Pull back wide shot showing basketball court"
                )
            ]

        return MasterPromptWorkflow(
            video_id=video_id,
            knowledge_point=knowledge_point,
            student_interest=student_interest,
            master_prompt_en=master_prompt,
            negative_prompt="blurry, distorted text, low quality, artifacts, glitch, noise",
            storyboard=storyboard,
            duration_seconds=30
        )


def create_ai_animation_workflow(
    knowledge_point: str,
    student_interest: str = "Minecraft"
) -> Dict[str, Any]:
    engine = ContextualMaterialEngine()
    res = engine.generate_video_workflow(knowledge_point=knowledge_point, student_interest=student_interest)
    return res.model_dump()
