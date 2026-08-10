# -*- coding: utf-8 -*-
"""
模块 2 Sigmoid 熔断算控单元测试 (test_fuse_sigmoid.py)
"""
import unittest
from backend.app.engine.fuse_sigmoid import check_meltdown_and_adjust, SigmoidMeltdownEngine


class TestSigmoidMeltdown(unittest.TestCase):

    def test_normal_progression(self):
        # 0 连错，低焦虑 -> 不触发熔断
        res = check_meltdown_and_adjust(consecutive_errors=0, frustration_level=0.1, current_difficulty=0.8)
        self.assertFalse(res["is_meltdown"])
        self.assertEqual(res["adjusted_difficulty"], 0.8)

    def test_meltdown_trigger(self):
        # 连错 4 题，高焦虑 0.8 -> 强制触发熔断，降低难度 50% 以上
        res = check_meltdown_and_adjust(consecutive_errors=4, frustration_level=0.8, current_difficulty=0.8)
        self.assertTrue(res["is_meltdown"])
        self.assertLess(res["adjusted_difficulty"], 0.4)
        self.assertEqual(res["action"], "TRIGGER_MELTDOWN_POPUP_AI_VIDEO")


if __name__ == "__main__":
    unittest.main()
