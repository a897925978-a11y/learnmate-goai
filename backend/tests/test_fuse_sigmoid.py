# -*- coding: utf-8 -*-
"""
v2.0 Sigmoid 熔断与 ZPD 心流单元测试 (test_fuse_sigmoid.py)
"""
import unittest
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust, ZPDFlowSigmoidEngine


class TestSigmoidMeltdown(unittest.TestCase):

    def test_normal_progression(self):
        res = check_meltdown_and_adjust(consecutive_errors=0, frustration_level=0.1, current_difficulty=0.8)
        self.assertFalse(res["is_meltdown"])

    def test_meltdown_trigger(self):
        res = check_meltdown_and_adjust(consecutive_errors=4, frustration_level=0.85, current_difficulty=0.85)
        self.assertTrue(res["is_meltdown"])
        self.assertEqual(res["zpd_zone"], "BELOW_ZPD_SHELTER")


if __name__ == "__main__":
    unittest.main()
