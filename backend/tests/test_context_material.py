# -*- coding: utf-8 -*-
"""
模块 5 & 模块 6 单元测试 (test_context_material.py & test_chroma_report.py)
"""
import unittest
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report, VectorReportTimeframe


class TestContextAndReport(unittest.TestCase):

    def test_context_video_workflow(self):
        res = create_ai_animation_workflow(knowledge_point="异分母分数加减法", student_interest="Minecraft")
        self.assertIsNotNone(res.video_id)
        self.assertEqual(res.duration_seconds, 30)
        self.assertIn("Minecraft", res.interest_context)
        self.assertGreaterEqual(len(res.visual_prompts), 1)

    def test_chroma_vector_report(self):
        res = build_academic_vector_report(student_id="STU-888", timeframe=VectorReportTimeframe.WEEKLY)
        self.assertEqual(res.student_id, "STU-888")
        self.assertIn("异分母分数加减法", res.mastery_radar)
        self.assertGreaterEqual(len(res.loop_adjustments), 1)


if __name__ == "__main__":
    unittest.main()
