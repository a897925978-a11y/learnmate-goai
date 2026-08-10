# -*- coding: utf-8 -*-
"""
心理学 FSM 与行为边界管制单元测试套件 (test_psychology_fsm.py)
"""
import unittest
from backend.app.engine.psychology_fsm import psychology_fsm_engine, BehaviorBoundaryCheckRequest


class TestPsychologyFSM(unittest.TestCase):

    def test_high_risk_hotline_override(self):
        req = BehaviorBoundaryCheckRequest(user_text="觉得自己活不下去了，好累")
        res = psychology_fsm_engine.check_behavior_boundary(req)
        self.assertEqual(res.boundary_status, "CRISIS_INTERCEPT")
        self.assertIn("400-161-9995", res.action_required)

    def test_sleep_lock(self):
        req = BehaviorBoundaryCheckRequest(current_hour=23)
        res = psychology_fsm_engine.check_behavior_boundary(req)
        self.assertEqual(res.boundary_status, "SLEEP_LOCK_TRIGGERED")

    def test_eye_protection(self):
        req = BehaviorBoundaryCheckRequest(screen_distance_cm=20.0)
        res = psychology_fsm_engine.check_behavior_boundary(req)
        self.assertEqual(res.boundary_status, "EYE_PROTECTION_WARN")


if __name__ == "__main__":
    unittest.main()
