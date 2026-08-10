# -*- coding: utf-8 -*-
"""
双端现象级推送与合规性单元测试套件 (test_dispatch_engine.py)
"""
import unittest
from backend.app.engine.dispatch_engine import dispatch_engine


class TestDualRoleDispatchEngine(unittest.TestCase):

    def test_evaluate_and_dispatch_compliance(self):
        alert = dispatch_engine.evaluate_and_dispatch(
            student_id="STU-2026",
            pause_duration_s=240.0,
            backspace_rate=9.5,
            user_input_text="异分母通分不会",
            screen_distance_cm=20.0,
            current_hour=21
        )

        self.assertIsNotNone(alert)
        self.assertTrue(alert.compliance_non_diagnostic_flag)
        self.assertIn("Parent", alert.target_roles)
        self.assertIn("Teacher", alert.target_roles)

        # 验证合规铁律：严禁包含心理学诊断词汇，只能是客观现象
        forbidden_words = ["焦虑症", "抑郁症", "心理不健康", "心理障碍", "智力缺陷"]
        for phenomenon in alert.observed_phenomena:
            self.assertTrue(phenomenon.startswith("观测现象："))
            for fw in forbidden_words:
                self.assertNotIn(fw, phenomenon)

    def test_no_alert_on_normal_behavior(self):
        alert = dispatch_engine.evaluate_and_dispatch(
            student_id="STU-2026",
            pause_duration_s=30.0,
            backspace_rate=2.0,
            user_input_text="正常做题",
            screen_distance_cm=40.0,
            current_hour=19
        )
        self.assertIsNone(alert)


if __name__ == "__main__":
    unittest.main()
