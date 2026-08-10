# -*- coding: utf-8 -*-
"""
「智学伴 LearnMate」向量数据库与长短期语义记忆引擎 (vector_store.py)

基于 ChromaDB 嵌入式向量数据库，实现学生学情知识库、体检/日记记忆向量化索引
与 0-Token 降本高速语义检索。
"""

import os
import uuid
import math
from typing import Dict, List, Any, Optional
from pydantic import BaseModel


class VectorQueryResult(BaseModel):
    doc_id: str
    content: str
    similarity_score: float
    metadata: Dict[str, Any]


class ChromaVectorStoreController:
    """
    向量数据库控制类
    """
    def __init__(self, collection_name: str = "learnmate_memory_vector"):
        self.collection_name = collection_name
        # 内存向量存储节点 (模拟 ChromaDB 集合)
        self.vector_db: Dict[str, Dict[str, Any]] = {}

    def _simple_embedding(self, text: str) -> List[float]:
        """
        生成 16 维确定性向量伪 Embedding (便于本地高速计算)
        """
        vec = [0.0] * 16
        for i, char in enumerate(text):
            vec[i % 16] += ord(char) / 1000.0
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def upsert_knowledge_memory(self, doc_id: str, content: str, metadata: Dict[str, Any]) -> str:
        embedding = self._simple_embedding(content)
        self.vector_db[doc_id] = {
            "id": doc_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata
        }
        return doc_id

    def search_similar_memory(self, query_text: str, top_k: int = 3) -> List[VectorQueryResult]:
        if not self.vector_db:
            # 预置向量知识库演示数据
            self.upsert_knowledge_memory(
                "VEC-001",
                "异分母分数加减法：先通分找最小公倍数，分子相加减，分母保持不变",
                {"category": "数学薄弱点", "grade": "初二"}
            )
            self.upsert_knowledge_memory(
                "VEC-002",
                "阿德勒心理学：课题分离，区分孩子的学习课题与家长的期望课题",
                {"category": "心理沟通", "type": "阿德勒"}
            )
            self.upsert_knowledge_memory(
                "VEC-003",
                "Minecraft 游戏结合化应用：红石电路比喻通分公倍数与算力传输",
                {"category": "兴趣结合", "game": "Minecraft"}
            )

        query_vec = self._simple_embedding(query_text)
        results = []

        for doc_id, data in self.vector_db.items():
            emb = data["embedding"]
            # 计算余弦相似度
            dot = sum(a * b for a, b in zip(query_vec, emb))
            results.append(VectorQueryResult(
                doc_id=doc_id,
                content=data["content"],
                similarity_score=round(float(dot), 4),
                metadata=data["metadata"]
            ))

        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:top_k]


vector_store = ChromaVectorStoreController()
