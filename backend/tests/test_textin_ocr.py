# -*- coding: utf-8 -*-
"""
TextIn 专业 OCR API 安全对接单元测试套件 (test_textin_ocr.py)
"""
import unittest
import os
from backend.app.engine.textin_ocr import textin_engine, get_textin_credentials


class TestTextInOCREngine(unittest.TestCase):

    def test_get_textin_credentials_security(self):
        app_id, secret_code = get_textin_credentials()
        self.assertIsNotNone(app_id)
        self.assertIsNotNone(secret_code)

    def test_textin_recognize_paper_image(self):
        res = textin_engine.recognize_paper_image(image_bytes=b"fake_test_image_bytes")
        self.assertIsNotNone(res.status)
        self.assertIn("选择题", res.raw_text)
        self.assertGreaterEqual(len(res.lines), 1)


if __name__ == "__main__":
    unittest.main()
