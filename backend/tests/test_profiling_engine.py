# -*- coding: utf-8 -*-
"""
全场景教育闭环全维档案引擎单元测试套件 (test_profiling_engine.py)
验证体检报告、日记情感随笔、学籍身份与全维度数据吸收功能
"""
import unittest
from backend.app.engine.profiling_engine import (
    profiling_engine,
    StudentIdentityRecord,
    MedicalCheckupRecord,
    StudentDiaryJournalRecord
)


class TestFullLifecycleProfilingEngine(unittest.TestCase):

    def test_ingest_full_student_data(self):
        identity = StudentIdentityRecord(
            student_id="STU-OMNI-001",
            student_name="吴同学",
            gender="男",
            age=14,
            school_name="实验中学",
            grade="初二",
            textbook_version="人教版",
            family_education_style="温和陪伴型"
        )

        health = MedicalCheckupRecord(
            checkup_date="2026-08-01",
            vision_left=4.5,
            vision_right=4.6,
            myopia_degrees_left=250,
            myopia_degrees_right=220,
            height_cm=168.0,
            weight_kg=55.0,
            average_sleep_hours=7.0,
            daily_exercise_steps=7500,
            health_notes="轻度近视，需定期控制屏幕时间"
        )

        diary = StudentDiaryJournalRecord(
            entry_date="2026-08-10",
            title="关于数学月考的小思考",
            content="今天试卷发下来了，异分母分数计算扣了分有点难过，但是弄懂通分后挺有成就感的！",
            peer_relationships_note="和同桌一起讨论了数学问题"
        )

        profile = profiling_engine.ingest_full_student_data(
            identity=identity,
            health_checkup=health,
            diary_entry=diary,
            interests=["Minecraft", "篮球", "机器人"],
            anxiety_score=3
        )

        self.assertEqual(profile.student_id, "STU-OMNI-001")
        self.assertTrue(profile.eye_protection_alert)  # 视力 4.5 < 4.8 触发护眼提醒
        self.assertEqual(len(profile.health_checkups), 1)
        self.assertEqual(len(profile.diaries_and_journals), 1)
        self.assertIn("轻度焦虑", profile.diaries_and_journals[0].detected_sentiment_tone)

    def test_add_diary_and_health_entry(self):
        diary = StudentDiaryJournalRecord(
            entry_date="2026-08-11",
            title="今天的练习体验",
            content="今天做题感觉很轻松，心态很好！"
        )
        res_diary = profiling_engine.add_diary_entry("STU-OMNI-001", diary)
        self.assertEqual(res_diary["status"], "SUCCESS")
        self.assertEqual(res_diary["detected_sentiment_tone"], "乐观")


if __name__ == "__main__":
    unittest.main()
