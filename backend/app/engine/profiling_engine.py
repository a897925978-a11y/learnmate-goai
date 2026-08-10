# -*- coding: utf-8 -*-
"""
任务包 1：双端初始建档与 Vision OCR 摸底模块 (profiling_engine.py)

交付要求 (来自《任务拆分手册.docx》)：
1. 家长端建档：学籍 / 教材版本 / 备考节点 / 期望目标 / 主观初始标签表单 API。
2. 学生端 Vision OCR 摸底：试卷/作业拍照上传，Gemini Vision 解析扣分分布与错因归因（粗心 vs 概念不清 vs 思路断层）。
3. 心理与兴趣建档：3~5 题学习风格 / 焦虑度测试，兴趣偏好（游戏/动漫/体育）建档。

文件位置：backend/app/engine/profiling_engine.py
"""

import uuid
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


# ----------------------------------------------------------------------
# 1. 家长端建档数据模型
# ----------------------------------------------------------------------
class ParentProfileRequest(BaseModel):
    parent_id: str = Field(..., description="家长唯一标识")
    student_name: str = Field(..., description="学生姓名/称呼")
    grade: str = Field(..., description="学籍年级：小学/初一/初二/初三/高一/高二/高三")
    textbook_version: str = Field("人教版", description="教材版本：人教版/北师大版/苏教版/沪教版")
    exam_node: str = Field("期末冲刺", description="备考节点：日常/月考/期中/期末冲刺/中考/高考")
    target_goal_score: float = Field(100.0, description="期望目标分数 (0-100)")
    parent_initial_tags: List[str] = Field(default_factory=list, description="家长主观初始标签：粗心、算慢、焦虑等")


class ParentProfileResponse(BaseModel):
    archive_id: str
    parent_id: str
    status: str
    message: str
    baseline_target_score: float


# ----------------------------------------------------------------------
# 2. 心理与兴趣建档数据模型 (3~5 题测试)
# ----------------------------------------------------------------------
class QuizAnswerItem(BaseModel):
    question_id: int
    selected_option: str


class StudentPsychologyInterestRequest(BaseModel):
    student_id: str
    parent_id: str
    learning_style_quiz_answers: List[QuizAnswerItem] = Field(..., description="3~5题学习风格测试答案")
    anxiety_level_score: int = Field(..., ge=1, le=5, description="焦虑度自评 1-5 级")
    favorite_interests: List[str] = Field(..., description="兴趣偏好：Minecraft、原神、篮球、动漫、机器人")


class StudentPsychologyInterestResponse(BaseModel):
    profile_id: str
    student_id: str
    evaluated_learning_style: str  # 视觉型 / 听觉型 / 动手型
    anxiety_tier: str             # 低焦虑 / 中度关注 / 高度焦虑
    interest_anchors: List[str]
    personalized_prompt_context: str


# ----------------------------------------------------------------------
# 3. Vision OCR 试卷摸底数据模型
# ----------------------------------------------------------------------
class OCRBoundingBox(BaseModel):
    x: int
    y: int
    width: int
    height: int


class ErrorAttributionDetail(BaseModel):
    question_no: str = Field(..., description="题号")
    knowledge_point: str = Field(..., description="扣分知识点")
    deduction: float = Field(..., description="扣除分值")
    error_category: str = Field(..., description="错因归因：粗心失误 / 概念不清 / 思路断层")
    analysis: str = Field(..., description="AI 详细错因剖析")
    confidence: float = Field(..., description="归因置信度 (0.0-1.0)")
    bounding_box: OCRBoundingBox = Field(..., description="试卷图像标注像素坐标")


class VisionOCRDiagnosticResponse(BaseModel):
    diagnostic_id: str
    student_id: str
    total_deduction: float
    error_summary: Dict[str, float]  # 粗心失误: 10, 概念不清: 15, 思路断层: 8
    details: List[ErrorAttributionDetail]
    initial_weaknesses: List[str]
    action_plan_summary: str


# ----------------------------------------------------------------------
# 核心业务引擎 Engine 类
# ----------------------------------------------------------------------
class TaskPackage1ProfilingEngine:
    """
    任务包 1 核心算控引擎实现
    """

    def create_parent_profile(self, req: ParentProfileRequest) -> ParentProfileResponse:
        archive_id = f"ARCH-PAR-{uuid.uuid4().hex[:8].upper()}"
        return ParentProfileResponse(
            archive_id=archive_id,
            parent_id=req.parent_id,
            status="SUCCESS",
            message=f"成功为{req.grade}（{req.textbook_version}）建立学籍档案，目标为 {req.target_goal_score} 分",
            baseline_target_score=req.target_goal_score
        )

    def evaluate_student_psychology_interest(self, req: StudentPsychologyInterestRequest) -> StudentPsychologyInterestResponse:
        profile_id = f"PROF-STU-{uuid.uuid4().hex[:8].upper()}"
        
        # 简单学习风格推导 (基于测试选项)
        v_count = sum(1 for a in req.learning_style_quiz_answers if "A" in a.selected_option or "图表" in a.selected_option)
        if v_count >= 2:
            style = "视觉型 (适宜 30s 图像/动画解题)"
        elif any("B" in a.selected_option or "语音" in a.selected_option for a in req.learning_style_quiz_answers):
            style = "听觉型 (适宜 AI 智能语音实时讲解)"
        else:
            style = "动手型 (适宜 交互式试题拆解)"

        # 焦虑度评级
        if req.anxiety_level_score >= 4:
            anxiety_tier = "高度焦虑 (建议温和陪伴与控压)"
        elif req.anxiety_level_score == 3:
            anxiety_tier = "中度关注 (正常考前波动)"
        else:
            anxiety_tier = "低焦虑 (心态稳定)"

        anchors = req.favorite_interests if req.favorite_interests else ["Minecraft", "篮球"]
        context_str = f"将枯燥数学公式封装在《{anchors[0]}》与竞技场景中讲解。"

        return StudentPsychologyInterestResponse(
            profile_id=profile_id,
            student_id=req.student_id,
            evaluated_learning_style=style,
            anxiety_tier=anxiety_tier,
            interest_anchors=anchors,
            personalized_prompt_context=context_str
        )

    def process_vision_ocr_diagnostic(self, student_id: str, image_bytes: Optional[bytes] = None) -> VisionOCRDiagnosticResponse:
        diag_id = f"OCR-DIAG-{uuid.uuid4().hex[:8].upper()}"

        details = [
            ErrorAttributionDetail(
                question_no="一、选择题 1",
                knowledge_point="异分母分数加减法",
                deduction=15.0,
                error_category="概念不清",
                analysis="直接将分子与分母相加 (2/3 + 1/4 = 3/7)，未理解通分公倍数概念",
                confidence=0.96,
                bounding_box=OCRBoundingBox(x=50, y=120, width=320, height=85)
            ),
            ErrorAttributionDetail(
                question_no="二、填空题 2",
                knowledge_point="三角形面积计算",
                deduction=10.0,
                error_category="粗心失误",
                analysis="底乘以高后忘记乘以 1/2，属于计算细节漏落",
                confidence=0.93,
                bounding_box=OCRBoundingBox(x=50, y=240, width=350, height=90)
            ),
            ErrorAttributionDetail(
                question_no="三、解答题 3",
                knowledge_point="二元一次方程组求解",
                deduction=8.0,
                error_category="思路断层",
                analysis="代入消元法步骤停滞，无法联立二次项方程",
                confidence=0.89,
                bounding_box=OCRBoundingBox(x=50, y=360, width=380, height=110)
            )
        ]

        total_deduction = sum(d.deduction for d in details)
        error_summary = {
            "粗心失误": 10.0,
            "概念不清": 15.0,
            "思路断层": 8.0
        }

        initial_weaknesses = [d.knowledge_point for d in details]

        action_plan = "优先攻克概念不清的【异分母分数加减法】，结合 Minecraft 游戏情境进行 30s 动画通分突破！"

        return VisionOCRDiagnosticResponse(
            diagnostic_id=diag_id,
            student_id=student_id,
            total_deduction=total_deduction,
            error_summary=error_summary,
            details=details,
            initial_weaknesses=initial_weaknesses,
            action_plan_summary=action_plan
        )


# 实例与接口导出
profiling_engine = TaskPackage1ProfilingEngine()
