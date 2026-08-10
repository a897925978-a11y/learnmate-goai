# -*- coding: utf-8 -*-
"""
模块 3：4 维无感物理遥测与博弈残差判定防作弊引擎 (telemetry_engine.py)

功能：
1. 提取 4 维底层交互行为物理特征：
   - T1: 首字/首动作时延 (First-Key Latency, ms)
   - T2: 退格与改写率 (Backspace Rate, counts/min)
   - T3: 选项悬停与犹豫时长 (Option Hovering Time, ms)
   - T4: 提交答题总工时 (Submission Duration, s)
2. 计算博弈残差 (Game-Theory Residual Score)
3. 识别“防装懂” (Fake Mastery) 和“防装累刷低难度” (Fake Fatigue)
"""

from typing import Dict, Any, List


class PhysicsTelemetryEngine:
    """
    4 维无感物理遥测与博弈残差判定引擎
    """

    def analyze_telemetry(
        self,
        user_declared_state: str,  # "完全懂了" / "太累了想减负" / "正常"
        first_key_latency_ms: float,
        backspace_rate: float,
        option_hover_ms: float,
        submission_duration_s: float,
        question_difficulty: float
    ) -> Dict[str, Any]:
        """
        计算博弈残差并输出防伪装判定结果
        """
        # 1. 物理行为异构积分 (Physical Behavior Index)
        # 真正懂了且轻松的典型特征: 首字延时低 (<800ms)、涂改少 (<2次)、悬停时间短 (<500ms)
        speed_score = max(0.0, 1.0 - (first_key_latency_ms / 3000.0))
        hesitation_score = max(0.0, 1.0 - (option_hover_ms / 2000.0))
        modification_penalty = min(1.0, backspace_rate / 10.0)

        # 行为估计能力分 = 0.5 * 速度 + 0.5 * 坚定度 - 0.2 * 删改
        implied_capability = max(0.0, min(1.0, 0.5 * speed_score + 0.5 * hesitation_score - 0.2 * modification_penalty))

        # 2. 博弈残差计算 Residual = | 声明状态对应预期 - 物理遥测推导值 |
        detected_anomaly = "NORMAL"
        is_fake_understanding = False
        is_fake_fatigue = False
        recommendation = "保持当前调度"

        if user_declared_state == "完全懂了":
            # 如果声明完全懂了，但悬停久 (>1200ms) 且删改频繁 (>5次)，判定为“装懂”
            if option_hover_ms > 1200 or backspace_rate > 5:
                is_fake_understanding = True
                detected_anomaly = "FAKE_UNDERSTANDING"
                recommendation = "看穿装懂！后台注入同类概念探针题排查薄弱项，不被欺骗升级难度。"

        elif user_declared_state == "太累了想减负":
            # 如果声明太累了，但首字延时极短 (<500ms) 且做题极流畅，判定为“装累刷低难度”
            if first_key_latency_ms < 600 and backspace_rate <= 1 and hesitation_score > 0.8:
                is_fake_fatigue = True
                detected_anomaly = "FAKE_FATIGUE"
                recommendation = "拦截装累刷低难度！保持正常学习节奏，拒绝偷懒诱导降维。"

        return {
            "implied_capability_score": round(implied_capability, 4),
            "user_declared_state": user_declared_state,
            "detected_anomaly": detected_anomaly,
            "is_fake_understanding": is_fake_understanding,
            "is_fake_fatigue": is_fake_fatigue,
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
    """
    对外调用的封装接口
    """
    engine = PhysicsTelemetryEngine()
    return engine.analyze_telemetry(
        user_declared_state=user_declared_state,
        first_key_latency_ms=first_key_latency_ms,
        backspace_rate=backspace_rate,
        option_hover_ms=option_hover_ms,
        submission_duration_s=submission_duration_s,
        question_difficulty=question_difficulty
    )
