# -*- coding: utf-8 -*-
"""
v2.0 模块 2 卡尔曼 + EWMA 去噪融合单元测试 (test_fuse_engine.py)
"""
import unittest
from backend.app.engine.fuse_engine import compute_fused_score, AdaptiveKalmanEWMADenoiser


class TestFuseEngine(unittest.TestCase):

    def test_adaptive_kalman_filtering(self):
        s_static = 0.5
        noise_spike = [0.2, 0.8, 0.1, 0.9, 0.15]
        res = compute_fused_score(s_static_history=s_static, s_dynamic_raw=noise_spike, N=5)

        self.assertIn("w_composite", res)
        self.assertIn("confidence_bounds", res)
        self.assertLessEqual(res["variance_suppression_ratio"], 0.35)


if __name__ == "__main__":
    unittest.main()
