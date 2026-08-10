# -*- coding: utf-8 -*-
"""
v2.0 (A,R) 心理学 FSM 与 Tier 3 400 热线单元测试 (test_psychology_fsm.py)
"""
import unittest
from backend.app.engine.psychology_fsm import process_psychology_fsm, EnhancedPsychologyFSMEngine


class TestPsychologyFSM(unittest.TestCase):

    def test_high_risk_hotline_override(self):
        res = process_psychology_fsm(user_input_text="我觉得活着没意思，想跳楼")
        self.assertTrue(res["is_crisis"])
        self.assertEqual(res["risk_tier"], "TIER_3_CLINICAL_HIGH_RISK")
        self.assertIn("400-161-9995", res["override_response"])

    def test_sleep_lock(self):
        res = process_psychology_fsm(user_input_text="我想做题", current_hour=23)
        self.assertFalse(res["is_crisis"])
        self.assertTrue(res["sleep_lock"]["is_locked"])


if __name__ == "__main__":
    unittest.main()
