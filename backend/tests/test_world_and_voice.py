# -*- coding: utf-8 -*-
"""
锁定世界模型与智能语音引擎单元测试套件 (test_world_and_voice.py)
"""
import unittest
from backend.app.engine.world_model_engine import world_model_engine
from backend.app.engine.voice_engine import voice_engine, VoiceChatRequest


class TestWorldAndVoiceEngines(unittest.TestCase):

    def test_world_model_prediction(self):
        res = world_model_engine.predict_pedagogical_world_state(
            student_id="STU-TEST",
            recent_concept="分数通分",
            current_score=65.0,
            frustration_level=0.3
        )
        self.assertIsNotNone(res.world_model_locked_name)
        self.assertIn("Qwen3.5-Omni", res.world_model_locked_name)
        self.assertGreater(res.zpd_difficulty_recommendation, 0.0)

    def test_voice_assistant_chat(self):
        req = VoiceChatRequest(
            student_id="STU-TEST",
            voice_input_text="异分母分数加减法怎么做？",
            interest_anchor="Minecraft"
        )
        res = voice_engine.process_voice_interaction(req)
        self.assertEqual(res.student_input_transcript, "异分母分数加减法怎么做？")
        self.assertIn("Minecraft", res.ai_voice_response_text)
        self.assertEqual(len(res.speech_audio_wave_preset), 10)


if __name__ == "__main__":
    unittest.main()
