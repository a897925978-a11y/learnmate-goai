# -*- coding: utf-8 -*-
"""
v2.0 模块 1 OCR 引擎单元测试 (test_ocr_engine.py)
"""
import unittest
from backend.app.engine.ocr_engine import analyze_test_paper_ocr, VisionOCREngine


class TestOCREngine(unittest.TestCase):

    def test_ocr_paper_processing(self):
        student_id = "STU-1001"
        res = analyze_test_paper_ocr(student_id=student_id, paper_image=b"fake_image_bytes")
        
        self.assertIsNotNone(res["archive_id"])
        self.assertIn("attribution_details", res)
        self.assertGreaterEqual(len(res["attribution_details"]), 1)
        self.assertEqual(res["attribution_details"][0]["knowledge_point"], "异分母分数加减法")


if __name__ == "__main__":
    unittest.main()
