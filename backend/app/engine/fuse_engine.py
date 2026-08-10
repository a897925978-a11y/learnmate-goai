# -*- coding: utf-8 -*-
"""
1D 卡尔曼滤波 + EWMA 动态心理分降噪算法模块 (fuse_engine.py)

该模块负责对学生学情过程中的动态原始得分 (s_dynamic_raw) 进行 1D 卡尔曼滤波与 EWMA 指数加权移动平均降噪，
并将降噪后的动态得分 (w_dynamic) 与静态历史分 (s_static_history) 按照 60:40 权重融合成最终复合得分 (w_composite)。
"""

from typing import List, Dict, Tuple, Any
import numpy as np


class KalmanEWMADenoiser:
    """
    1D 卡尔曼滤波 + EWMA 联合降噪引擎
    """
    def __init__(
        self,
        process_noise_Q: float = 1e-4,
        measurement_noise_R: float = 0.04,
        ewma_alpha: float = 0.3
    ):
        """
        :param process_noise_Q: 过程噪声方差 Q (超参依据：假设学生真实学情能力平稳微变)
        :param measurement_noise_R: 测量噪声方差 R (超参依据：假设单题表现存在约 0.2 的偶发波动)
        :param ewma_alpha: EWMA 平滑系数 alpha (0 < alpha <= 1)
        """
        self.Q = process_noise_Q
        self.R = measurement_noise_R
        self.alpha = ewma_alpha

    def filter_signal(self, raw_scores: List[float]) -> List[float]:
        """
        对原始动态得分离散序列进行 1D 卡尔曼滤波 + EWMA 串联降噪
        """
        if not raw_scores:
            return []

        # 1. 第一阶段：1D 卡尔曼滤波 (Kalman Filter)
        x_est = raw_scores[0]  # 初始状态估计
        P_est = 1.0            # 初始协方差
        kalman_filtered = []

        for z in raw_scores:
            # 预测更新 (Predict)
            x_pred = x_est
            P_pred = P_est + self.Q

            # 测量更新 (Update)
            K = P_pred / (P_pred + self.R)  # 卡尔曼增益
            x_est = x_pred + K * (z - x_pred)
            P_est = (1.0 - K) * P_pred

            kalman_filtered.append(float(x_est))

        # 2. 第二阶段：EWMA 指数平滑 (EWMA Smoothing)
        ewma_filtered = []
        s_prev = kalman_filtered[0]
        for val in kalman_filtered:
            s_curr = self.alpha * val + (1.0 - self.alpha) * s_prev
            ewma_filtered.append(float(s_curr))
            s_prev = s_curr

        return ewma_filtered


def compute_fused_score(
    s_static_history: float,
    s_dynamic_raw: List[float],
    N: int = 5,
    process_noise_Q: float = 1e-4,
    measurement_noise_R: float = 0.04,
    ewma_alpha: float = 0.3
) -> Dict[str, Any]:
    """
    契约实现函数:
    Input: {s_static_history, s_dynamic_raw, N}
    Output: {w_composite, w_dynamic, filtered_series, variance_suppression_ratio}

    :param s_static_history: 静态历史得分基线 (0.0 - 1.0)
    :param s_dynamic_raw: 动态原始得分序列 (0.0 - 1.0)
    :param N: 滑动窗口长度 (取最新 N 项进行计算)
    :return: 包含 w_composite 与 w_dynamic 的字典结果
    """
    if not s_dynamic_raw:
        w_dyn = float(s_static_history)
        w_comp = float(s_static_history)
        return {
            "w_composite": round(w_comp, 4),
            "w_dynamic": round(w_dyn, 4),
            "filtered_series": [],
            "variance_suppression_ratio": 0.0
        }

    # 截取最新 N 项
    window_data = s_dynamic_raw[-N:] if len(s_dynamic_raw) > N else s_dynamic_raw

    # 实例化联合降噪引擎
    denoiser = KalmanEWMADenoiser(
        process_noise_Q=process_noise_Q,
        measurement_noise_R=measurement_noise_R,
        ewma_alpha=ewma_alpha
    )

    # 滤波降噪处理
    filtered_series = denoiser.filter_signal(window_data)
    w_dynamic = filtered_series[-1]

    # 60:40 复合融合算控
    w_composite = 0.6 * w_dynamic + 0.4 * s_static_history

    # 方差抑制率计算 (用于测试断言: 跳变方差抑制)
    raw_var = float(np.var(window_data)) if len(window_data) > 1 else 0.0
    filtered_var = float(np.var(filtered_series)) if len(filtered_series) > 1 else 0.0
    
    # 输出方差相对于原始方差的比率 (即残留方差比)
    var_ratio = (filtered_var / raw_var) if raw_var > 0 else 0.0

    return {
        "w_composite": round(float(w_composite), 4),
        "w_dynamic": round(float(w_dynamic), 4),
        "filtered_series": [round(x, 4) for x in filtered_series],
        "variance_suppression_ratio": round(float(var_ratio), 4)
    }
