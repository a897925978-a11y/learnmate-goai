"""
EduLoop Agent - 标准 API 接口定义模型 (Pydantic Models)
涵盖 6 大核心模块与主控 Agent 数据交互规范
"""

from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


# ==========================================
# 阶段 1 / 模块 1：首次双端建档与 OCR 摸底
# ==========================================

class GradeLevel(str, Enum):
    PRIMARY = "primary"        # 小学
    JUNIOR = "junior"          # 初中
    SENIOR = "senior"          # 高中

class ExamNode(str, Enum):
    SEMESTER_START = "semester_start"  # 刚开学
    MONTHLY = "monthly"                # 月考前
    MIDTERM = "midterm"                # 期中冲刺
    FINAL = "final"                    # 期末备考
    ENTRANCE = "entrance"              # 中高考

class ParentArchiveRequest(BaseModel):
    parent_id: str = Field(..., description="家长唯一标识")
    grade: GradeLevel = Field(..., description="年级")
    textbook_version: str = Field("人教版", description="教材版本")
    target_subject: str = Field("数学", description="目标学科")
    exam_node: ExamNode = Field(ExamNode.MONTHLY, description="备考节点")
    target_goal: str = Field("冲刺提分", description="期望目标")
    parent_tags: List[str] = Field(default_factory=list, description="家长主观给孩子打的标签（如：粗心、数学吃力）")
    reward_setting: Optional[str] = Field(None, description="完成闭环后的奖励设置")

class StudentArchiveRequest(BaseModel):
    student_id: str = Field(..., description="学生唯一标识")
    parent_id: str = Field(..., description="绑定的家长标识")
    learning_style: str = Field("视觉型", description="心理学学习风格（视觉/听觉/动手型）")
    interests: List[str] = Field(default_factory=lambda: ["游戏", "动漫"], description="兴趣偏好（如：Minecraft, 篮球）")
    exam_anxiety_level: int = Field(3, ge=1, le=5, description="考试焦虑度（1-5级）")

class OCRDiagnosticResponse(BaseModel):
    archive_id: str = Field(..., description="成长档案 ID")
    extracted_text: str = Field(..., description="Vision OCR 识别出的试卷文本")
    deduction_points: Dict[str, float] = Field(..., description="扣分知识点分布")
    error_attribution: Dict[str, str] = Field(..., description="错因归因（粗心/概念模糊/解题无思路）")
    initial_weaknesses: List[str] = Field(..., description="初始薄弱知识点列表")


# ==========================================
# 模块 2：每日隐形微摸底与三层隐私屏障
# ==========================================

class DailyCheckinRequest(BaseModel):
    student_id: str = Field(..., description="学生 ID")
    raw_response: Optional[str] = Field(None, description="学生对微问候的对话回复")
    is_refused: bool = Field(False, description="学生是否避而不答/拒绝回复")

class PrivacyLevel(str, Enum):
    DESENSITIZED = "desensitized"  # 脱敏归纳
    AUTHORIZED = "authorized"      # 双向授权
    CRISIS_OVERRIDE = "crisis"     # 危机穿透

class PrivacyShieldResponse(BaseModel):
    privacy_level: PrivacyLevel
    emotional_index: float = Field(..., description="当日情绪指数 (0-100)")
    perceived_stress_source: str = Field(..., description="脱敏后的压力源类型")
    parent_notice: str = Field(..., description="给家长的安全提示（隐去私人秘密）")
    is_crisis_alert: bool = Field(False, description="是否触发高危预警")


# ==========================================
# 模块 3：心理学大师亲子桥梁智库
# ==========================================

class PerceptionGapAnalysis(BaseModel):
    parent_perception: List[str] = Field(..., description="家长主观标签")
    student_reality: List[str] = Field(..., description="学生真实摸底心声与错因")
    gap_score: float = Field(..., description="认知错位度 (0-100)")

class PsychologyMasterAdviceResponse(BaseModel):
    gap_analysis: PerceptionGapAnalysis
    quoted_master: str = Field(..., description="引用的心理学大师（如：阿德勒、卡尔·罗杰斯）")
    theory_quote: str = Field(..., description="大师经典名言/理论引用")
    parent_guidance: str = Field(..., description="权威亲子沟通破冰指南")


# ==========================================
# 模块 4：兴趣情境资料与 AI 视频工作流接口 (荆广伟接口)
# ==========================================

class ContextualMaterialRequest(BaseModel):
    knowledge_point: str = Field(..., description="目标知识点")
    student_interest: str = Field(..., description="调用的学生兴趣情境（如：Minecraft 伤害计算）")

class AIVideoWorkflowMetadata(BaseModel):
    video_id: str = Field(..., description="视频唯一 ID")
    knowledge_point: str = Field(..., description="知识点")
    interest_context: str = Field(..., description="兴趣情境描述")
    audio_script: str = Field(..., description="给 AI 视频渲染的旁白脚本")
    visual_prompts: List[str] = Field(..., description="给 ComfyUI/Runway 的画面 Prompt")
    duration_seconds: int = Field(30, description="建议视频时长")


# ==========================================
# 模块 5：Gemini Live 实时音视频陪伴与三态 UI
# ==========================================

class UIStateMode(str, Enum):
    PERSONA_COMPANION = "persona"  # 拟人化 AI 学伴/导师
    FLOATING_WIDGET = "floating"   # 做题悬浮窗/轻卡片
    GAME_LEVEL_MAP = "game_map"    # 游戏化关卡地图

class LiveCompanionConfig(BaseModel):
    student_id: str
    active_mode: UIStateMode = Field(UIStateMode.PERSONA_COMPANION)
    companion_tone: str = Field("知心导师", description="匹配的沟通语气（知心导师/严格教练）")

class AttentionMonitorFrame(BaseModel):
    attention_score: float = Field(..., description="注意力集中度 (0-100)")
    fatigue_detected: bool = Field(False, description="是否检测到疲劳")
    posture_warning: Optional[str] = Field(None, description="姿态提醒（如：坐姿太低）")


# ==========================================
# 模块 6：Chroma 向量学情诊断与双端闭环
# ==========================================

class VectorReportTimeframe(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    ANNUAL = "annual"

class MultiScaleReportResponse(BaseModel):
    student_id: str
    timeframe: VectorReportTimeframe
    mastery_radar: Dict[str, float] = Field(..., description="各知识能力维度掌握度 (0-100)")
    emotional_trend: List[float] = Field(..., description="长周期情绪波动趋势")
    growth_summary: str = Field(..., description="长周期成长轨迹总结")
    loop_adjustments: List[str] = Field(..., description="反哺下阶段教案与资料的调整建议")
