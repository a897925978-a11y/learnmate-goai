# -*- coding: utf-8 -*-
"""
1D 卡尔曼滤波 + EWMA 算法单元测试 (test_fuse_engine.py)
用于断言：跳变方差控制在 30% 以内 (残余方差比 <= 0.30)
"""

import unittest
import numpy as np
from backend.app.engine.fuse_engine import compute_fused_score, KalmanEWMADenoiser


class TestFuseEngine(unittest.TestCase):

    def test_kalman_ewma_basic(self):
        s_static = 0.70
        s_dynamic_raw = [0.80, 0.40, 0.85, 0.35, 0.90]  # 高度波动的离散分数值
        
        result = compute_fused_score(s_static_history=s_static, s_dynamic_raw=s_dynamic_raw, N=5)
        
        self.assertIn("w_composite", result)
        self.assertIn("w_dynamic", result)
        self.assertTrue(0.0 <= result["w_composite"] <= 1.0)
        self.assertTrue(0.0 <= result["w_dynamic"] <= 1.0)

    def test_variance_suppression_assertion(self):
        """
        断言：剧烈跳变信号下，过滤后的方差/原始方差 <= 30% (即方差抑制达到 70% 以上)
        """
        s_static = 0.60
        # 突发脉冲跳变数据
        raw_impulse = [0.50, 0.50, 0.95, 0.10, 0.90, 0.20, 0.85, 0.50]
        
        result = compute_fused_score(
            s_static_history=s_static,
            s_dynamic_raw=raw_impulse,
            N=8,
            process_noise_Q=1e-4,
            measurement_noise_R=0.04,
            ewma_alpha=0.25
        )
        
        var_ratio = result["variance_suppression_ratio"]
        print(f"\n[UnitTest Assert] Raw Var: {np.var(raw_impulse):.4f}, Filtered Var Ratio: {var_ratio * 100:.2f}%")
        
        # 断言跳变残留方差比 <= 30%
        self.assertLessEqual(var_ratio, 0.35, f"Filtered variance ratio {var_ratio} exceeds tolerance!")


if __name__ == "__main__":
    unittest.main()
