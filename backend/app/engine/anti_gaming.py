# -*- coding: utf-8 -*-
"""
DEV-T3-A: 4 维无感行为物理遥测提取引擎 (anti_gaming.py)
所属模块: 模块3 — 无感遥测与抗作弊

=====================================================================
对抗式审查结论（第一性原则，不重复造轮子）:
---------------------------------------------------------------------
backend/app/engine/telemetry_engine.py 已实现「物理遥测马氏距离与熵特征」引擎，
其输入维度为 (first_key_latency_ms, backspace_rate, option_hover_ms, submission_duration_s)，
输出基于物理动作(退格率/悬停时长/首字延迟)的异常分类。

本模块是模块3「无感遥测与抗作弊」的 **文本/交互级补充**，按工单契约输入 4 维:
    {first_token_latency_ms, edit_distance_ratio, hover_count, response_time_sec}
其中 **edit_distance_ratio（答题删改编辑距离比）是 telemetry_engine 完全不具备的新维度**，
它刻画「作答过程中反复涂改/推翻重来」的文本级行为，是识别「装懂」的高危信号。

因此本模块独立实现，不重写 telemetry_engine，二者信号源互补:
    - telemetry_engine : 物理动作级 (退格率 / 悬停时长 / 首字延迟)
    - anti_gaming      : 文本编辑级 (edit_distance_ratio) + 交互级 (hover_count) + 时序级
输出统一的结构化 telemetry_metrics 字典，供后端直接消费。
=====================================================================
"""

import math
from typing import Dict, Any


def _levenshtein(a: str, b: str) -> int:
    """标准 Levenshtein 编辑距离 (DP)。空串/相等做快速短路。"""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    return prev[-1]


def compute_edit_distance_ratio(draft_text: str, final_text: str) -> float:
    """计算答题草稿 -> 最终文本的归一化编辑距离比 [0, 1]。

    edit_distance_ratio = Levenshtein(draft, final) / max(1, len(final))
    取值越高代表作答过程中反复涂改 / 推翻重来，是「装懂」的高危文本信号。
    该函数使引擎自包含: 既能接收采集层预计算的 ratio，也能基于原始文本自行计算。
    """
    final_len = max(1, len((final_text or "").strip()))
    dist = _levenshtein(draft_text or "", final_text or "")
    return min(1.0, max(0.0, dist / final_len))


class AntiGamingTelemetryEngine:
    """4 维无感行为物理遥测提取引擎（模块3 抗作弊）。

    契约输入: first_token_latency_ms, edit_distance_ratio, hover_count, response_time_sec
    契约输出: 结构化 telemetry_metrics 字典（传递给后端）
    """

    # 各维度的归一化分母（基于产品实测分布的工程阈值）
    _LATENCY_CEIL_MS = 3500.0   # 首字延迟上限，超过即视为严重卡顿
    _HOVER_CEIL = 12.0          # 悬停次数上限
    _RESPONSE_CEIL_S = 120.0    # 响应时长上限，超过即视为极度犹豫

    def extract_telemetry(
        self,
        first_token_latency_ms: float,
        edit_distance_ratio: float,
        hover_count: int,
        response_time_sec: float,
        user_declared_state: str = "未知",
    ) -> Dict[str, Any]:
        """提取 4 维无感行为遥测，合成结构化 telemetry_metrics。

        Returns:
            {
              "telemetry_metrics": {  # 结构化指标，传递给后端
                  "first_token_fluency": float,   # 首字流畅度 [0,1]
                  "edit_distance_ratio": float,   # 编辑距离比 [0,1]（核心新维度）
                  "hover_intensity": float,       # 悬停强度 [0,1]
                  "response_pace": float,         # 响应节奏 [0,1]
                  "gaming_risk_score": float,     # 装懂/博弈风险分 [0,1]
                  "detected_gaming_pattern": str, # NORMAL/FAKE_UNDERSTANDING/RANDOM_GUESSING/HESITATION_REWRITE
                  "is_likely_faking": bool,
                  "recommendation": str,
              },
              "raw_input": {...}  # 回显原始契约输入，便于溯源
            }
        """
        # 1. 4 维标准化归一
        v_fluency = min(1.0, max(0.0, 1.0 - (float(first_token_latency_ms) / self._LATENCY_CEIL_MS)))
        v_edit = min(1.0, max(0.0, float(edit_distance_ratio)))
        v_hover = min(1.0, max(0.0, float(hover_count) / self._HOVER_CEIL))
        v_pace = min(1.0, max(0.0, 1.0 - (float(response_time_sec) / self._RESPONSE_CEIL_S)))

        # 2. 合成装懂 / 博弈风险分
        #    核心: edit_distance_ratio 主导（反复涂改 = 装懂高危），叠加首字卡顿与悬停犹豫
        gaming_risk = max(0.0, min(1.0,
            0.50 * v_edit
            + 0.25 * (1.0 - v_fluency)
            + 0.25 * v_hover
        ))

        # 3. 异常模式判定（纯行为信号，无感、不依赖用户自述状态）
        detected = "NORMAL"
        is_likely_faking = False
        if v_edit >= 0.45 and (1.0 - v_fluency) >= 0.55:
            detected = "FAKE_UNDERSTANDING"
            is_likely_faking = True
        elif float(first_token_latency_ms) < 300 and int(hover_count) <= 1 and float(response_time_sec) < 8:
            detected = "RANDOM_GUESSING"
        elif v_edit >= 0.60:
            detected = "HESITATION_REWRITE"  # 反复涂改但不一定装懂，需讲解干预
            is_likely_faking = True

        telemetry_metrics: Dict[str, Any] = {
            "first_token_fluency": round(v_fluency, 4),
            "edit_distance_ratio": round(v_edit, 4),
            "hover_intensity": round(v_hover, 4),
            "response_pace": round(v_pace, 4),
            "gaming_risk_score": round(gaming_risk, 4),
            "detected_gaming_pattern": detected,
            "is_likely_faking": is_likely_faking,
            "recommendation": self._recommend(detected),
        }

        return {
            "telemetry_metrics": telemetry_metrics,
            "raw_input": {
                "first_token_latency_ms": first_token_latency_ms,
                "edit_distance_ratio": edit_distance_ratio,
                "hover_count": hover_count,
                "response_time_sec": response_time_sec,
                "user_declared_state": user_declared_state,
            },
        }

    @staticmethod
    def _recommend(pattern: str) -> str:
        return {
            "NORMAL": "作答行为自然，遥测正常，保持正常调度。",
            "FAKE_UNDERSTANDING": "看穿装懂：作答反复涂改且首字严重卡顿，保持当前难度排查薄弱项。",
            "RANDOM_GUESSING": "检测到极速盲选蒙题，作废本题数据并重新弹题测试。",
            "HESITATION_REWRITE": "检测到反复涂改，建议插入知识点讲解视频消除卡点。",
        }.get(pattern, "作答行为正常。")


def extract_anti_gaming_telemetry(
    first_token_latency_ms: float,
    edit_distance_ratio: float,
    hover_count: int,
    response_time_sec: float,
    user_declared_state: str = "未知",
) -> Dict[str, Any]:
    """便捷函数：按契约计算结构化 telemetry_metrics 传递给后端。"""
    return AntiGamingTelemetryEngine().extract_telemetry(
        first_token_latency_ms=first_token_latency_ms,
        edit_distance_ratio=edit_distance_ratio,
        hover_count=hover_count,
        response_time_sec=response_time_sec,
        user_declared_state=user_declared_state,
    )
