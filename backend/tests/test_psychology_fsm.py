# -*- coding: utf-8 -*-
"""
模块 4 (A,R) 心理学 FSM 与 Tier 3 400 热线硬阻断单元测试 (test_psychology_fsm.py)
"""
import unittest
from backend.app.engine.psychology_fsm import process_psychology_fsm, PsychologyFSMEngine


class TestPsychologyFSM(unittest.TestCase):

    def test_high_risk_hotline_override(self):
        # 输入高危词汇 -> 100% 触发 Tier 3 硬阻断并弹出 400 热线
        res = process_psychology_fsm(user_input_text="我觉得活着没意思，想跳楼")
        self.assertTrue(res["is_crisis"])
        self.assertEqual(res["action"], "TIER_3_HARD_BLOCK_HOTLINE_OVERRIDE")
        self.assertIn("400-161-9995", res["override_response"])

    def test_sleep_lock(self):
        # 23:00 深夜 -> 触发睡眠保护锁
        res = process_psychology_fsm(user_input_text="我想做题", current_hour=23)
        self.assertFalse(res["is_crisis"])
        self.assertTrue(res["sleep_lock"]["is_locked"])
        self.assertIn("太晚了", res["sleep_lock"]["lock_message"])

    def test_adler_guidance(self):
        # 正常状态 -> 生成阿德勒破冰指南
        res = process_psychology_fsm(user_input_text="数学第三题怎么做", current_hour=19)
        self.assertFalse(res["is_crisis"])
        self.assertIn("阿德勒", res["adler_guidance"]["quoted_master"])


if __name__ == "__main__":
    unittest.main()
