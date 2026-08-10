# -*- coding: utf-8 -*-
"""
模块 2 (Part B)：Sigmoid 非线性相变熔断与破冰卡弹窗逻辑引擎 (fuse_sigmoid.py)

功能：
1. 监控学生连续答错次数 (consecutive_errors) 与考前焦虑指数 (frustration_score)
2. 通过 Sigmoid 函数计算非线性崩溃概率 P_meltdown
3. 触发“防崩溃熔断”：强制将题目难度降低 50% 以上，并弹窗推送 30 秒线上 AI 动画短视频讲透知识点
"""

import math
from typing import Dict, Any, List


def sigmoid(x: float) -> float:
    """
    Sigmoid 激活函数 S(x) = 1 / (1 + exp(-x))
    """
    return 1.0 / (1.0 + math.exp(-x))


class SigmoidMeltdownEngine:
    """
    Sigmoid 相变防崩溃熔断算控引擎
    """
    def __init__(self, threshold: float = 0.65, k: float = 2.5, x0: float = 3.0):
        """
        :param threshold: 熔断触发概率阈值 (默认 0.65)
        :param k: Sigmoid 增益斜率 (控制相变急剧程度)
        :param x0: 相变中点拐点 (连续错 3 题为相变中心)
        """
        self.threshold = threshold
        self.k = k
        self.x0 = x0

    def evaluate_meltdown_risk(
        self,
        consecutive_errors: int,
        frustration_level: float,  # 0.0 - 1.0
        current_difficulty: float  # 0.0 - 1.0
    ) -> Dict[str, Any]:
        """
        计算相变熔断概率并返回调降后的难度与动作指令
        """
        # 综合相变输入指标 x = k * (consecutive_errors - x0) + 2.0 * frustration_level
        x = self.k * (consecutive_errors - self.x0) + 2.0 * frustration_level
        p_meltdown = sigmoid(x)

        is_meltdown = p_meltdown >= self.threshold

        if is_meltdown:
            # 强制降低难度 50% 以上 (最低降至 0.2)
            adjusted_difficulty = max(0.2, current_difficulty * 0.45)
            action = "TRIGGER_MELTDOWN_POPUP_AI_VIDEO"
            message = "⚠️ 检测到情绪重挫，已为您强制降低难度 50%，并为您调取 30 秒线上 AI 动画解析短视频！"
        else:
            adjusted_difficulty = current_difficulty
            action = "NORMAL_PROGRESSION"
            message = "学情状态平稳，按正常 ZPD 心流节奏推题。"

        return {
            "p_meltdown": round(p_meltdown, 4),
            "is_meltdown": is_meltdown,
            "original_difficulty": current_difficulty,
            "adjusted_difficulty": round(adjusted_difficulty, 4),
            "action": action,
            "message": message
        }


def check_meltdown_and_adjust(
    consecutive_errors: int,
    frustration_level: float,
    current_difficulty: float = 0.8
) -> Dict[str, Any]:
    """
    对外调用的封装接口
    """
    engine = SigmoidMeltdownEngine()
    return engine.evaluate_meltdown_risk(
        consecutive_errors=consecutive_errors,
        frustration_level=frustration_level,
        current_difficulty=current_difficulty
    )
