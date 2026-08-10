# -*- coding: utf-8 -*-
"""
v2.0 模块 5 & 模块 6 单元测试 (test_context_material.py)
"""
import unittest
from backend.app.engine.context_material import create_ai_animation_workflow
from backend.app.engine.chroma_report import build_academic_vector_report


class TestContextAndReport(unittest.TestCase):

    def test_context_video_workflow(self):
        res = create_ai_animation_workflow(knowledge_point="异分母分数加减法", student_interest="Minecraft")
        self.assertIsNotNone(res["video_id"])
        self.assertEqual(res["duration_seconds"], 30)
        self.assertIn("master_prompt_en", res)
        self.assertGreaterEqual(len(res["storyboard"]), 1)

    def test_chroma_vector_report(self):
        res = build_academic_vector_report(student_id="STU-888", timeframe="weekly")
        self.assertEqual(res["student_id"], "STU-888")
        self.assertIn("mastery_radar", res)
        self.assertIn("weakness_tree", res)


if __name__ == "__main__":
    unittest.main()
