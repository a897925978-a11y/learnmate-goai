# -*- coding: utf-8 -*-
"""
模块 3 4维无感物理遥测防作弊单元测试 (test_telemetry_engine.py)
"""
import unittest
from backend.app.engine.telemetry_engine import process_physics_telemetry


class TestPhysicsTelemetry(unittest.TestCase):

    def test_fake_understanding_detection(self):
        # 声明“完全懂了”，但悬停 1500ms，改写 8 次 -> 判定为 FAKE_UNDERSTANDING
        res = process_physics_telemetry(
            user_declared_state="完全懂了",
            first_key_latency_ms=1200,
            backspace_rate=8.0,
            option_hover_ms=1500,
            submission_duration_s=45
        )
        self.assertTrue(res["is_fake_understanding"])
        self.assertEqual(res["detected_anomaly"], "FAKE_UNDERSTANDING")

    def test_fake_fatigue_detection(self):
        # 声明“太累了想减负”，但首字 400ms，改写 0 次，极其流畅 -> 判定为 FAKE_FATIGUE
        res = process_physics_telemetry(
            user_declared_state="太累了想减负",
            first_key_latency_ms=400,
            backspace_rate=0.0,
            option_hover_ms=200,
            submission_duration_s=15
        )
        self.assertTrue(res["is_fake_fatigue"])
        self.assertEqual(res["detected_anomaly"], "FAKE_FATIGUE")


if __name__ == "__main__":
    unittest.main()
