# -*- coding: utf-8 -*-
"""
v2.0 模块 2 卡尔曼 + EWMA 去噪融合单元测试 (test_fuse_engine.py)
补强（DEV-T2-A / WorkBuddy）：
- 将 variance_suppression_ratio 断言上限由 0.35 收紧至 0.30，与工单/任务包手册口径一致；
- 增补边界(空/单元素/N越界)、平稳、渐变用例，守护回归；
- 渐变用例断言 var_ratio < 0.30（实测约 0.16），避免滤波削平趋势导致比率虚高漏测。
"""
import unittest
from backend.app.engine.fuse_engine import compute_fused_score, AdaptiveKalmanEWMADenoiser

VAR_CAP = 0.30  # 工单/任务包手册要求：跳变方差 < 30%


class TestFuseEngine(unittest.TestCase):

    def test_adaptive_kalman_filtering(self):
        """脉冲噪声跳变（算法强项用例，原测试守护）"""
        s_static = 0.5
        noise_spike = [0.2, 0.8, 0.1, 0.9, 0.15]
        res = compute_fused_score(s_static_history=s_static, s_dynamic_raw=noise_spike, N=5)

        self.assertIn("w_composite", res)
        self.assertIn("confidence_bounds", res)
        self.assertLessEqual(res["variance_suppression_ratio"], VAR_CAP)

    def test_empty_input(self):
        """空动态序列：应回退到静态分，不产生 NaN/异常"""
        res = compute_fused_score(s_static_history=0.5, s_dynamic_raw=[], N=5)
        self.assertEqual(res["w_composite"], 0.5)
        self.assertEqual(res["w_dynamic"], 0.5)
        self.assertEqual(res["variance_suppression_ratio"], 0.0)
        self.assertEqual(res["filtered_series"], [])

    def test_single_element(self):
        """单元素动态序列：边界不崩，比率定义为零"""
        res = compute_fused_score(s_static_history=0.5, s_dynamic_raw=[0.5], N=5)
        self.assertAlmostEqual(res["w_dynamic"], 0.5, places=4)
        self.assertAlmostEqual(res["variance_suppression_ratio"], 0.0, places=4)

    def test_window_larger_than_length(self):
        """N 大于序列长度：应取全序列，不越界不报错"""
        res = compute_fused_score(s_static_history=0.5, s_dynamic_raw=[0.3, 0.9, 0.2], N=10)
        self.assertLessEqual(res["variance_suppression_ratio"], VAR_CAP)

    def test_steady_low_variance(self):
        """平稳低方差输入：比率在口径内（低原始方差下比率可能虚高，已 docstring 说明）"""
        res = compute_fused_score(s_static_history=0.5, s_dynamic_raw=[0.49, 0.51, 0.50, 0.52, 0.50], N=5)
        self.assertLessEqual(res["variance_suppression_ratio"], VAR_CAP)

    def test_ramp_transition(self):
        """渐变输入：滤波会削平趋势，但比率仍须 < 30%（实测约 0.16）"""
        res = compute_fused_score(s_static_history=0.5, s_dynamic_raw=[0.3, 0.4, 0.5, 0.6, 0.7], N=5)
        self.assertLessEqual(res["variance_suppression_ratio"], VAR_CAP)


if __name__ == "__main__":
    unittest.main()
