# -*- coding: utf-8 -*-
"""
模块 1 OCR 引擎单元测试 (test_ocr_engine.py)
"""
import unittest
from backend.app.engine.ocr_engine import analyze_test_paper_ocr, VisionOCREngine


class TestOCREngine(unittest.TestCase):

    def test_ocr_paper_processing(self):
        student_id = "STU-1001"
        res = analyze_test_paper_ocr(student_id=student_id, paper_image=b"fake_image_bytes")
        
        self.assertIsNotNone(res.archive_id)
        self.assertIn("异分母分数加减法", res.deduction_points)
        self.assertIn("概念模糊", res.error_attribution["异分母分数加减法"])
        self.assertGreaterEqual(len(res.initial_weaknesses), 1)


if __name__ == "__main__":
    unittest.main()
