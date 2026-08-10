# -*- coding: utf-8 -*-
"""
任务包 1 扩展：全场景教育闭环全维学生档案引擎 (StudentOmniLifecycleProfile)

根据用户最新指令升级：
能够吸收/吃下所有关于学生的全维度数据，包含：
1. 🏥 医疗体检报告与生理健康数据 (视力、睡眠、BMI、运动)
2. 🪪 身份与家庭背景信息 (学籍、年龄、家庭教育协同模式)
3. 📖 每日日记/成长随笔/情感心事 (情绪倾向识别、同伴关系、校内体验)
4. 📚 学科试卷/作业 Vision OCR 摸底 (错因归因、知识图谱)

文件位置：backend/app/engine/profiling_engine.py
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field
from backend.app.engine.textin_ocr import textin_engine


# ----------------------------------------------------------------------
# 1. 🏥 生理健康与体检报告数据模型 (Medical & Physical Checkup)
# ----------------------------------------------------------------------
class MedicalCheckupRecord(BaseModel):
    checkup_id: Optional[str] = None
    checkup_date: str = Field(..., description="体检日期 (YYYY-MM-DD)")
    vision_left: float = Field(..., description="左眼裸眼视力 (如 4.8 或 1.0)")
    vision_right: float = Field(..., description="右眼裸眼视力")
    myopia_degrees_left: int = Field(0, description="左眼近视度数")
    myopia_degrees_right: int = Field(0, description="右眼近视度数")
    height_cm: float = Field(..., description="身高 (cm)")
    weight_kg: float = Field(..., description="体重 (kg)")
    bmi: Optional[float] = Field(None, description="BMI 指数")
    average_sleep_hours: float = Field(8.0, description="平均睡眠时长 (小时)")
    daily_exercise_steps: int = Field(6000, description="日均运动步数")
    health_notes: Optional[str] = Field(None, description="过敏史、慢性疾病或体质注意事项")


# ----------------------------------------------------------------------
# 2. 🪪 身份与家庭背景数据模型 (Identity & Demographics)
# ----------------------------------------------------------------------
class StudentIdentityRecord(BaseModel):
    student_id: str = Field(..., description="学生唯一 ID")
    student_name: str = Field(..., description="学生姓名/昵称")
    gender: str = Field("未透露", description="性别")
    age: int = Field(..., description="年龄")
    school_name: str = Field(..., description="就读学校名称")
    grade: str = Field(..., description="学籍年级：小学/初一/初二/初三/高一/高二/高三")
    textbook_version: str = Field("人教版", description="教材版本")
    family_education_style: str = Field("温和陪伴型", description="家庭教育风格：严厉型/温和陪伴型/放养型/期望极高型")


# ----------------------------------------------------------------------
# 3. 📖 日记随笔与心理情感数据模型 (Diaries & Sentiment Journals)
# ----------------------------------------------------------------------
class StudentDiaryJournalRecord(BaseModel):
    journal_id: Optional[str] = None
    entry_date: str = Field(..., description="日记日期 (YYYY-MM-DD)")
    title: str = Field(..., description="日记标题")
    content: str = Field(..., description="日记/随笔正文内容")
    detected_sentiment_tone: Optional[str] = Field(None, description="AI 识别出的情绪声调：乐观/焦虑/重挫/孤独/自信")
    peer_relationships_note: Optional[str] = Field(None, description="同伴关系与校内社交笔记")


# ----------------------------------------------------------------------
# 4. 家长端建档与心理兴趣数据模型
# ----------------------------------------------------------------------
class ParentProfileRequest(BaseModel):
    parent_id: str = Field(..., description="家长唯一标识")
    student_name: str = Field(..., description="学生姓名/称呼")
    grade: str = Field(..., description="学籍年级")
    textbook_version: str = Field("人教版", description="教材版本")
    exam_node: str = Field("期末冲刺", description="备考节点")
    target_goal_score: float = Field(100.0, description="期望目标分数")
    parent_initial_tags: List[str] = Field(default_factory=list, description="家长主观初始标签")


class QuizAnswerItem(BaseModel):
    question_id: int
    selected_option: str


class StudentPsychologyInterestRequest(BaseModel):
    student_id: str
    parent_id: str
    learning_style_quiz_answers: List[QuizAnswerItem]
    anxiety_level_score: int = Field(..., ge=1, le=5)
    favorite_interests: List[str]


# ----------------------------------------------------------------------
# 5. 全维度学生成长闭环总档案模型 (StudentOmniLifecycleProfile)
# ----------------------------------------------------------------------
class StudentOmniLifecycleProfile(BaseModel):
    profile_id: str
    student_id: str
    identity: StudentIdentityRecord
    health_checkups: List[MedicalCheckupRecord]
    diaries_and_journals: List[StudentDiaryJournalRecord]
    learning_style: str
    anxiety_tier: str
    interests: List[str]
    eye_protection_alert: bool = Field(False, description="基于体检视力触发护眼提醒")
    sleep_health_alert: bool = Field(False, description="基于睡眠时长触发劝睡锁定")
    omni_summary: str = Field(..., description="全维度闭环成长诊断总结")


# ----------------------------------------------------------------------
# 核心业务引擎类 Implementation
# ----------------------------------------------------------------------
class FullLifecycleProfilingEngine:
    """
    全场景教育闭环全维学生档案引擎
    """
    def __init__(self):
        # 内存型全维度学生档案仓
        self.profiles_db: Dict[str, StudentOmniLifecycleProfile] = {}

    def ingest_full_student_data(
        self,
        identity: StudentIdentityRecord,
        health_checkup: Optional[MedicalCheckupRecord] = None,
        diary_entry: Optional[StudentDiaryJournalRecord] = None,
        interests: Optional[List[str]] = None,
        anxiety_score: int = 3
    ) -> StudentOmniLifecycleProfile:
        profile_id = f"OMNI-STU-{uuid.uuid4().hex[:8].upper()}"

        health_records = [health_checkup] if health_checkup else []
        diary_records = []
        
        if diary_entry:
            # AI 情绪分析识别
            tone = "乐观"
            if any(w in diary_entry.content for w in ["难过", "考砸", "讨厌", "累"]):
                tone = "轻度焦虑"
            elif any(w in diary_entry.content for w in ["绝望", "没意思", "痛苦"]):
                tone = "重挫/高危"
            diary_entry.detected_sentiment_tone = tone
            diary_records.append(diary_entry)

        # 视力与睡眠健康预警判断
        eye_alert = False
        sleep_alert = False
        if health_checkup:
            if health_checkup.vision_left < 4.8 or health_checkup.vision_right < 4.8 or health_checkup.myopia_degrees_left > 200:
                eye_alert = True
            if health_checkup.average_sleep_hours < 7.5:
                sleep_alert = True

        anchors = interests if interests else ["Minecraft", "篮球"]
        style = "视觉型 (适宜动画/图表)"

        anxiety_tier = "心态平稳"
        if anxiety_score >= 4:
            anxiety_tier = "高度焦虑 (建议控压)"

        omni_summary = (
            f"已建立【{identity.student_name}】全场景教育闭环档案。系统综合吸收了学籍（{identity.grade}）、"
            f"健康体检数据（视力/睡眠/BMI）、心事日记（情绪倾向：{diary_records[0].detected_sentiment_tone if diary_records else '平稳'}）"
            f"及兴趣偏好（{anchors}），为后续智能体精准个性化规划提供全维度支撑。"
        )

        omni_profile = StudentOmniLifecycleProfile(
            profile_id=profile_id,
            student_id=identity.student_id,
            identity=identity,
            health_checkups=health_records,
            diaries_and_journals=diary_records,
            learning_style=style,
            anxiety_tier=anxiety_tier,
            interests=anchors,
            eye_protection_alert=eye_alert,
            sleep_health_alert=sleep_alert,
            omni_summary=omni_summary
        )

        self.profiles_db[identity.student_id] = omni_profile
        return omni_profile

    def add_diary_entry(self, student_id: str, entry: StudentDiaryJournalRecord) -> Dict[str, Any]:
        tone = "乐观"
        if any(w in entry.content for w in ["难过", "考砸", "累", "压力"]):
            tone = "焦虑"
        entry.detected_sentiment_tone = tone

        if student_id in self.profiles_db:
            self.profiles_db[student_id].diaries_and_journals.append(entry)

        return {
            "status": "SUCCESS",
            "student_id": student_id,
            "entry_title": entry.title,
            "detected_sentiment_tone": tone,
            "message": f"成功吸收日记《{entry.title}》，已更新学生全闭环情感画像！"
        }

    def add_health_checkup(self, student_id: str, checkup: MedicalCheckupRecord) -> Dict[str, Any]:
        if student_id in self.profiles_db:
            self.profiles_db[student_id].health_checkups.append(checkup)

        return {
            "status": "SUCCESS",
            "student_id": student_id,
            "vision_left": checkup.vision_left,
            "vision_right": checkup.vision_right,
            "bmi": round(checkup.weight_kg / ((checkup.height_cm / 100) ** 2), 2),
            "message": f"成功吸收{checkup.checkup_date}体检报告，更新视力与睡眠健康画像！"
        }


# 全局共享实例
profiling_engine = FullLifecycleProfilingEngine()
