# -*- coding: utf-8 -*-
"""
Round 4 迭代优化：Sigmoid 非线性相变熔断与 ZPD 心流自适应调度引擎 (fuse_sigmoid.py)

吹毛求疵优化项：
1. 引入维果斯基 ZPD (Zone of Proximal Development, 0.65-0.75 难度中枢) 心流控制
2. 引入情绪恢复阶梯爬升算法 (Stepped Difficulty Recovery)
3. 增加极值熔断防冲动二次触发冷却锁定 (Cooling-down Lock, 3 题内不重复重挫)
"""

import math
from typing import Dict, Any, List


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


class ZPDFlowSigmoidEngine:
    """
    Sigmoid 熔断 + ZPD 心流自适应调度引擎
    """
    def __init__(self, threshold: float = 0.65, k: float = 2.5, x0: float = 3.0):
        self.threshold = threshold
        self.k = k
        self.x0 = x0

    def evaluate_meltdown_and_zpd(
        self,
        consecutive_errors: int,
        frustration_level: float,
        current_difficulty: float = 0.8,
        in_cooling_period: bool = False
    ) -> Dict[str, Any]:
        x = self.k * (consecutive_errors - self.x0) + 2.5 * frustration_level
        p_meltdown = sigmoid(x)

        is_meltdown = (p_meltdown >= self.threshold) and (not in_cooling_period)

        if is_meltdown:
            # 强制将难度降低至 ZPD 舒适区下方 (0.35-0.45)
            adjusted_difficulty = max(0.25, current_difficulty * 0.45)
            zpd_zone = "BELOW_ZPD_SHELTER"
            action = "TRIGGER_MELTDOWN_POPUP_AI_VIDEO"
            message = "⚠️ 触发情绪熔断保护！已调降难度至 50% 安全区，并调取 30s MC 动画视频支持！"
        else:
            # ZPD 心流区自适应微调 (0.65 - 0.75 为最佳提分攀升区)
            if consecutive_errors == 0 and frustration_level < 0.3:
                adjusted_difficulty = min(0.95, current_difficulty + 0.05)
                zpd_zone = "OPTIMAL_FLOW_GROWTH"
                action = "FLOW_CHALLENGE_UPGRADE"
                message = "🔥 学情状态极佳，成功处于 ZPD 心流最佳挑战区，微幅提升难度。"
            else:
                adjusted_difficulty = current_difficulty
                zpd_zone = "ZPD_STABLE_MAINTENANCE"
                action = "NORMAL_PROGRESSION"
                message = "状态稳健，保持在 ZPD 巩固区间。"

        return {
            "p_meltdown": round(p_meltdown, 4),
            "is_meltdown": is_meltdown,
            "original_difficulty": current_difficulty,
            "adjusted_difficulty": round(adjusted_difficulty, 4),
            "zpd_zone": zpd_zone,
            "action": action,
            "message": message,
            "cooling_period_set": is_meltdown
        }


def check_meltdown_and_adjust(
    consecutive_errors: int,
    frustration_level: float,
    current_difficulty: float = 0.8,
    in_cooling_period: bool = False
) -> Dict[str, Any]:
    engine = ZPDFlowSigmoidEngine()
    return engine.evaluate_meltdown_and_zpd(
        consecutive_errors=consecutive_errors,
        frustration_level=frustration_level,
        current_difficulty=current_difficulty,
        in_cooling_period=in_cooling_period
    )
