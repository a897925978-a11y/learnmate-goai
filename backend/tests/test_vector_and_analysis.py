# -*- coding: utf-8 -*-
"""
向量数据库与专门分析 API 单元测试套件 (test_vector_and_analysis.py)
"""
import unittest
from backend.app.engine.vector_store import vector_store
from backend.app.engine.analysis_engine import analysis_engine


class TestVectorAndAnalysisEngines(unittest.TestCase):

    def test_vector_store_upsert_and_query(self):
        doc_id = vector_store.upsert_knowledge_memory(
            doc_id="TEST-VEC-01",
            content="测试概念：勾股定理 a^2 + b^2 = c^2",
            metadata={"subject": "数学"}
        )
        self.assertEqual(doc_id, "TEST-VEC-01")

        results = vector_store.search_similar_memory("勾股定理", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertIsNotNone(results[0].similarity_score)

    def test_deep_academic_analysis(self):
        report = analysis_engine.run_deep_academic_analysis(
            student_id="STU-2026",
            recent_test_scores=[60.0, 70.0, 65.0],
            identified_errors=["异分母分数加减法"],
            diary_sentiment="轻度焦虑"
        )
        self.assertEqual(report.student_id, "STU-2026")
        self.assertEqual(len(report.weakness_graph), 2)
        self.assertEqual(report.weakness_graph[0].action_priority_index, 95)
        self.assertIn("最小公倍数", report.weakness_graph[0].prerequisite_nodes[0])


if __name__ == "__main__":
    unittest.main()
