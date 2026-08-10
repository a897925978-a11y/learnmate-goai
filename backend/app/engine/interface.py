# -*- coding: utf-8 -*-
"""
抽象接口层 (Public Interface Boundary)
公开库只保留接口定义与 Pydantic 模型，核心实现放在私有化层
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any


class AbstractDenoiseEngine(ABC):
    """
    学情降噪抽象基类 (接口契约)
    """

    @abstractmethod
    def filter_signal(self, raw_scores: List[float]) -> List[float]:
        pass

    @abstractmethod
    def compute_fused_score(self, s_static_history: float, s_dynamic_raw: List[float], N: int = 5) -> Dict[str, Any]:
        pass
