# -*- coding: utf-8 -*-
"""
任务包 1 单元测试套件 (test_profiling_engine.py)
验证家长端建档、心理与兴趣测试、Vision OCR 试卷摸底全量 API 契约
"""
import unittest
from backend.app.engine.profiling_engine import (
    profiling_engine,
    ParentProfileRequest,
    StudentPsychologyInterestRequest,
    QuizAnswerItem
)


class TestTaskPackage1ProfilingEngine(unittest.TestCase):

    def test_create_parent_profile(self):
        req = ParentProfileRequest(
            parent_id="PAR-1001",
            student_name="小明",
            grade="初二",
            textbook_version="人教版",
            exam_node="期末冲刺",
            target_goal_score=95.0,
            parent_initial_tags=["粗心", "缺乏耐性"]
        )
        res = profiling_engine.create_parent_profile(req)
        self.assertEqual(res.status, "SUCCESS")
        self.assertEqual(res.parent_id, "PAR-1001")
        self.assertEqual(res.baseline_target_score, 95.0)

    def test_evaluate_student_psychology_interest(self):
        answers = [
            QuizAnswerItem(question_id=1, selected_option="A. 看动画/图表"),
            QuizAnswerItem(question_id=2, selected_option="A. 视觉演示"),
            QuizAnswerItem(question_id=3, selected_option="B. 听老师解说")
        ]
        req = StudentPsychologyInterestRequest(
            student_id="STU-2026",
            parent_id="PAR-1001",
            learning_style_quiz_answers=answers,
            anxiety_level_score=4,
            favorite_interests=["Minecraft", "篮球"]
        )
        res = profiling_engine.evaluate_student_psychology_interest(req)
        self.assertIn("视觉型", res.evaluated_learning_style)
        self.assertIn("高度焦虑", res.anxiety_tier)
        self.assertIn("Minecraft", res.interest_anchors)

    def test_process_vision_ocr_diagnostic(self):
        res = profiling_engine.process_vision_ocr_diagnostic(student_id="STU-2026", image_bytes=b"fake_image")
        self.assertEqual(res.student_id, "STU-2026")
        self.assertEqual(res.total_deduction, 33.0)
        self.assertIn("概念不清", res.error_summary)
        self.assertEqual(len(res.details), 3)
        self.assertEqual(res.details[0].question_no, "一、选择题 1")


if __name__ == "__main__":
    unittest.main()
