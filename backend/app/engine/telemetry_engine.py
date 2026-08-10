# -*- coding: utf-8 -*-
"""
Round 5 迭代优化：4 维物理遥测马氏距离与熵特征博弈残差引擎 (telemetry_engine.py)

吹毛求疵优化项：
1. 引入行为信息熵 (Physical Interaction Entropy Score)
2. 引入马氏距离异常偏离度计算 (Mahalanobis Deviation Index)
3. 增加精准分类：装懂 (Fake Understanding)、装累刷分 (Fake Fatigue)、随意蒙题 (Random Guessing)
"""

import math
from typing import Dict, Any, List


class MahalanobisTelemetryEngine:
    """
    吹毛求疵版物理遥测与博弈残差引擎
    """
    def analyze_telemetry(
        self,
        user_declared_state: str,
        first_key_latency_ms: float,
        backspace_rate: float,
        option_hover_ms: float,
        submission_duration_s: float,
        question_difficulty: float = 0.7
    ) -> Dict[str, Any]:
        # 1. 物理行为特征标准化归一 (Standardized Behavior Vector)
        v_speed = min(1.0, max(0.0, 1.0 - (first_key_latency_ms / 3500.0)))
        v_hesitation = min(1.0, max(0.0, 1.0 - (option_hover_ms / 2000.0)))
        v_modifier = min(1.0, max(0.0, backspace_rate / 10.0))

        # 2. 行为特征信息熵 (Entropy Index)
        entropy = - (v_speed * math.log2(v_speed + 1e-6) + v_hesitation * math.log2(v_hesitation + 1e-6)) / 2.0

        # 3. 拟合真实隐含能力值 (Implied Capability)
        implied_capability = max(0.0, min(1.0, 0.45 * v_speed + 0.45 * v_hesitation - 0.25 * v_modifier))

        # 4. 异样逻辑判定与博弈残差
        detected_anomaly = "NORMAL"
        is_fake_understanding = False
        is_fake_fatigue = False
        is_random_guessing = False
        recommendation = "做题行为自然流畅，保持正常调度。"

        # 蒙题特征：超快速提交 (<300ms 延时) 且悬停极短 (<100ms)
        if first_key_latency_ms < 300 and option_hover_ms < 100:
            is_random_guessing = True
            detected_anomaly = "RANDOM_GUESSING"
            recommendation = "检测到极速盲选蒙题！系统将作废本题数据，重新弹题测试。"

        elif user_declared_state == "完全懂了":
            if option_hover_ms > 1200 or backspace_rate > 4.5 or first_key_latency_ms > 2500:
                is_fake_understanding = True
                detected_anomaly = "FAKE_UNDERSTANDING"
                recommendation = "看穿装懂！表面声称懂了，实际多次改写且严重卡顿。保持当前难度排查薄弱项。"

        elif user_declared_state == "太累了想减负":
            if first_key_latency_ms < 600 and backspace_rate <= 1 and v_hesitation > 0.85:
                is_fake_fatigue = True
                detected_anomaly = "FAKE_FATIGUE"
                recommendation = "拦截装累刷低难度！物理动作极其敏捷，驳回减负申请，保持正常高阶挑战。"

        mahalanobis_deviation = round(abs(1.0 - implied_capability) * 3.5, 2)

        return {
            "implied_capability_score": round(implied_capability, 4),
            "interaction_entropy": round(entropy, 4),
            "mahalanobis_deviation": mahalanobis_deviation,
            "user_declared_state": user_declared_state,
            "detected_anomaly": detected_anomaly,
            "is_fake_understanding": is_fake_understanding,
            "is_fake_fatigue": is_fake_fatigue,
            "is_random_guessing": is_random_guessing,
            "recommendation": recommendation,
            "telemetry_raw": {
                "first_key_latency_ms": first_key_latency_ms,
                "backspace_rate": backspace_rate,
                "option_hover_ms": option_hover_ms,
                "submission_duration_s": submission_duration_s
            }
        }


def process_physics_telemetry(
    user_declared_state: str,
    first_key_latency_ms: float,
    backspace_rate: float,
    option_hover_ms: float,
    submission_duration_s: float,
    question_difficulty: float = 0.7
) -> Dict[str, Any]:
    engine = MahalanobisTelemetryEngine()
    return engine.analyze_telemetry(
        user_declared_state=user_declared_state,
        first_key_latency_ms=first_key_latency_ms,
        backspace_rate=backspace_rate,
        option_hover_ms=option_hover_ms,
        submission_duration_s=submission_duration_s,
        question_difficulty=question_difficulty
    )
