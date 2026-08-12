# -*- coding: utf-8 -*-
"""
DEV-T3-A 单元测试 (test_anti_gaming.py)
单测断言: 成功计算结构化 telemetry_metrics 传递给后端

运行: 仓库根目录执行
    python -m unittest backend.tests.test_anti_gaming
"""
import unittest
from backend.app.engine.anti_gaming import (
    compute_edit_distance_ratio,
    extract_anti_gaming_telemetry,
    AntiGamingTelemetryEngine,
)


class TestAntiGamingTelemetry(unittest.TestCase):

    def test_compute_edit_distance_ratio_identical(self):
        # 草稿与最终一致 -> 编辑距离比为 0
        self.assertAlmostEqual(compute_edit_distance_ratio("答案是B", "答案是B"), 0.0, places=4)

    def test_compute_edit_distance_ratio_rewrite(self):
        # 草稿被大幅改写 -> 编辑距离比落在 (0, 1]
        ratio = compute_edit_distance_ratio("我认为是A因为", "正确答案应为C，理由是")
        self.assertTrue(0.0 < ratio <= 1.0)

    def test_compute_edit_distance_ratio_empty_final(self):
        # 最终文本为空时，分母兜底为 1，不除零
        self.assertEqual(compute_edit_distance_ratio("abc", ""), 1.0)

    def test_fake_understanding_detection(self):
        # 编辑距离比高(反复涂改) + 首字严重卡顿 -> FAKE_UNDERSTANDING
        res = extract_anti_gaming_telemetry(
            first_token_latency_ms=3000,
            edit_distance_ratio=0.6,
            hover_count=9,
            response_time_sec=80,
        )
        metrics = res["telemetry_metrics"]
        self.assertIsInstance(metrics, dict)
        self.assertTrue(metrics["is_likely_faking"])
        self.assertEqual(metrics["detected_gaming_pattern"], "FAKE_UNDERSTANDING")
        # 结构化 telemetry_metrics 必须含 4 维 + 风险分（传递给后端的契约）
        for k in ("first_token_fluency", "edit_distance_ratio", "hover_intensity",
                  "response_pace", "gaming_risk_score"):
            self.assertIn(k, metrics)

    def test_random_guessing_detection(self):
        # 极速盲选: 首字极快、几乎不悬停、响应极短 -> RANDOM_GUESSING
        res = extract_anti_gaming_telemetry(
            first_token_latency_ms=200,
            edit_distance_ratio=0.05,
            hover_count=0,
            response_time_sec=5,
        )
        self.assertEqual(res["telemetry_metrics"]["detected_gaming_pattern"], "RANDOM_GUESSING")

    def test_hesitation_rewrite_detection(self):
        # 极高编辑距离比但首字不算卡顿 -> HESITATION_REWRITE（反复涂改需讲解干预）
        res = extract_anti_gaming_telemetry(
            first_token_latency_ms=1500,
            edit_distance_ratio=0.85,
            hover_count=4,
            response_time_sec=60,
        )
        self.assertEqual(res["telemetry_metrics"]["detected_gaming_pattern"], "HESITATION_REWRITE")
        self.assertTrue(res["telemetry_metrics"]["is_likely_faking"])

    def test_normal_behavior(self):
        # 自然作答 -> NORMAL，且 raw_input 回显契约字段
        res = extract_anti_gaming_telemetry(
            first_token_latency_ms=800,
            edit_distance_ratio=0.1,
            hover_count=3,
            response_time_sec=30,
        )
        metrics = res["telemetry_metrics"]
        self.assertEqual(metrics["detected_gaming_pattern"], "NORMAL")
        self.assertFalse(metrics["is_likely_faking"])
        self.assertIn("raw_input", res)
        self.assertEqual(res["raw_input"]["hover_count"], 3)


if __name__ == "__main__":
    unittest.main()
