# -*- coding: utf-8 -*-
"""
心理学 FSM 与行为边界管制单元测试套件 (test_psychology_fsm.py)
"""
import unittest
from backend.app.engine.psychology_fsm import (
    psychology_fsm_engine,
    BehaviorBoundaryCheckRequest,
    CRISIS_DIRECT_TERMS,
    CRISIS_UI_ACTION,
    CRISIS_SEMANTIC_THRESHOLD,
)


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


class TestDEV_T4_B_CrisisSafetyBarrier(unittest.TestCase):
    """DEV-T4-B 契约断言：语义匹配>=0.90 -> is_ai_blocked=True, ui_action=RENDER_HOTLINE_400_161_9995"""

    def test_crisis_schema_fields(self):
        """危机命中时返回机器可读契约字段"""
        req = BehaviorBoundaryCheckRequest(user_text="我最近总是想自残")
        res = psychology_fsm_engine.check_behavior_boundary(req)
        self.assertTrue(res.is_ai_blocked)
        self.assertEqual(res.ui_action, CRISIS_UI_ACTION)
        self.assertGreaterEqual(res.semantic_match_score, CRISIS_SEMANTIC_THRESHOLD)
        self.assertTrue(res.matched_terms)

    def test_self_harm_100pct_block(self):
        """断言：遇到自残等词汇时 100% 阻断 AI 对话（遍历全部 direct 高危词）"""
        for term in CRISIS_DIRECT_TERMS:
            with self.subTest(term=term):
                res = psychology_fsm_engine.check_behavior_boundary(
                    BehaviorBoundaryCheckRequest(user_text=f"我有点{term}的念头")
                )
                self.assertTrue(res.is_ai_blocked, f"高危词[{term}]未阻断")
                self.assertEqual(res.ui_action, CRISIS_UI_ACTION)

    def test_crisis_synonym_block(self):
        """强近义改写说法同样跨 0.90 阈值触发阻断"""
        res = psychology_fsm_engine.check_behavior_boundary(
            BehaviorBoundaryCheckRequest(user_text="有时候真想伤害自己")
        )
        self.assertTrue(res.is_ai_blocked)
        self.assertEqual(res.ui_action, CRISIS_UI_ACTION)
        self.assertGreaterEqual(res.semantic_match_score, CRISIS_SEMANTIC_THRESHOLD)

    def test_benign_no_block(self):
        """良性文本不阻断，ui_action 为空"""
        res = psychology_fsm_engine.check_behavior_boundary(
            BehaviorBoundaryCheckRequest(user_text="今天数学函数题终于搞懂了，很开心")
        )
        self.assertFalse(res.is_ai_blocked)
        self.assertIsNone(res.ui_action)
        self.assertEqual(res.semantic_match_score, 0.0)

    def test_evaluate_crisis_safety_contract(self):
        """契约方法直接返回 Agent_7 口径：is_ai_blocked/ui_action/alert_encrypted_payload"""
        result = psychology_fsm_engine.evaluate_crisis_safety("活着没意思，想结束生命")
        self.assertTrue(result.is_ai_blocked)
        self.assertEqual(result.ui_action, CRISIS_UI_ACTION)
        self.assertGreaterEqual(result.semantic_match_score, CRISIS_SEMANTIC_THRESHOLD)
        self.assertEqual(result.alert_encrypted_payload, "CRISIS_EVENT_LOG_ENCRYPTED")


if __name__ == "__main__":
    unittest.main()
