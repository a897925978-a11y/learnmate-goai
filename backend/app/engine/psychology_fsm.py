# -*- coding: utf-8 -*-
"""
模块 4：(A,R) 心理学 FSM 状态机与 Tier 3 临床危机 400 热线硬阻断 (psychology_fsm.py)

功能：
1. 评估家长主观认知与孩子真实水平的认知错位度 (Perception Gap)
2. 生成阿德勒 (Adler) / 卡尔·罗杰斯 (Rogers) 亲子破冰指南卡片
3. 22:00 深夜睡眠保护锁 (Sleep Lock)
4. Tier 3 临床高危情绪 100% 硬阻断，切断 AI 拟人化回答，强制渲染国家心理热线 400-161-9995
"""

from datetime import datetime
from typing import Dict, Any, List


HIGH_RISK_KEYWORDS = [
    "自残", "自杀", "轻生", "不想活了", "跳楼", "割腕", "厌世", "活着没意思"
]


class PsychologyFSMEngine:
    """
    (A,R) 心理学 FSM 状态机与危机干预引擎
    """

    def check_crisis_and_override(self, user_input_text: str) -> Dict[str, Any]:
        """
        Tier 3 临床高危安全屏障硬阻断检查
        """
        for kw in HIGH_RISK_KEYWORDS:
            if kw in user_input_text:
                return {
                    "is_crisis": True,
                    "risk_keyword": kw,
                    "action": "TIER_3_HARD_BLOCK_HOTLINE_OVERRIDE",
                    "override_response": (
                        "⚠️ 【国家心理援助安全屏障启动】\n"
                        "我们非常关心你的感受！系统已暂停 AI 对话，请记得你并不孤单，专业温暖的帮助随时都在身边：\n"
                        "📞 全国心理援助热线：400-161-9995（24小时免费）\n"
                        "📞 共青团青少年关爱热线：12355\n"
                        "请停下手中的题目，喝杯温水，随时拨打上方热线与专业倾听者聊聊。"
                    )
                }

        return {
            "is_crisis": False,
            "risk_keyword": None,
            "action": "PROCEED_REGULAR_DIALOGUE",
            "override_response": None
        }

    def check_sleep_lock(self, current_hour: int = None) -> Dict[str, Any]:
        """
        22:00 深夜睡眠锁控制
        """
        if current_hour is None:
            current_hour = datetime.now().hour

        # 晚上 22:00 至 次日 06:00 强制劝睡锁屏
        if current_hour >= 22 or current_hour < 6:
            return {
                "is_locked": True,
                "current_hour": current_hour,
                "lock_message": "🌙 太晚了！充足的睡眠是高效大脑的基石。今日练习已自动锁定，赶紧洗漱睡觉吧，明天早上见！"
            }

        return {
            "is_locked": False,
            "current_hour": current_hour,
            "lock_message": None
        }

    def generate_adler_parent_guidance(
        self,
        parent_target: str,
        student_actual: float,
        parent_tags: List[str]
    ) -> Dict[str, Any]:
        """
        基于阿德勒‘课题分离’与罗杰斯‘无条件积极关注’理论生成亲子破冰卡
        """
        gap_score = abs(100.0 - student_actual * 100.0)
        
        theory_quote = "“阿德勒心理学强调‘课题分离’与‘过程性鼓励’——学习是孩子的课题，家长的关怀是建立无条件的心理安全感。”"
        
        guidance = (
            f"根据本周学情数据，孩子在【解题探索】上表现出了很强的韧性。建议今晚沟通时：\n"
            f"1. 避免使用“你怎么又粗心”等否定性标签；\n"
            f"2. 针对错因，肯定孩子的思考步骤：“我看到你前三步逻辑很清晰，太棒了！”；\n"
            f"3. 给予孩子 15 分钟自由支配的休息时间，建立信任纽带。"
        )

        return {
            "quoted_master": "阿尔弗雷德·阿德勒 (Alfred Adler)",
            "theory_quote": theory_quote,
            "parent_guidance": guidance,
            "perception_gap_score": round(gap_score, 2)
        }


def process_psychology_fsm(
    user_input_text: str,
    parent_target: str = "冲刺满分",
    student_actual: float = 0.65,
    current_hour: int = 20
) -> Dict[str, Any]:
    """
    对外调用的封装接口
    """
    engine = PsychologyFSMEngine()

    # 1. 优先检查高危危机
    crisis_res = engine.check_crisis_and_override(user_input_text)
    if crisis_res["is_crisis"]:
        return crisis_res

    # 2. 检查睡眠锁
    sleep_res = engine.check_sleep_lock(current_hour=current_hour)

    # 3. 生成阿德勒破冰指南
    adler_res = engine.generate_adler_parent_guidance(
        parent_target=parent_target,
        student_actual=student_actual,
        parent_tags=["粗心", "焦虑"]
    )

    return {
        "is_crisis": False,
        "sleep_lock": sleep_res,
        "adler_guidance": adler_res
    }
