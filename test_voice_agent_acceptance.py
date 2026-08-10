# -*- coding: utf-8 -*-
"""
[司法级独立验收测试脚本] test_voice_agent_acceptance.py
专用于自动化审计“实时多语言语音智能体”代码交付质量
"""

import time
import requests
import json
import sys
import io

# 设置 Windows 标准输出为 UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://127.0.0.1:8000"

def test_01_api_health_check():
    """验证 REST 主页及健康检查"""
    t0 = time.time()
    r = requests.get(f"{BASE_URL}/")
    latency_ms = (time.time() - t0) * 1000
    assert r.status_code == 200, "服务主页未正常响应 200 OK"
    print(f"[Test 1 PASS] 基础服务连通性正常，延迟: {latency_ms:.1f}ms")

def test_02_multilingual_short_spoken_responses():
    """验证多语言精炼口语对答 (1-2 句短句，拒绝书面大段灌水，正确识别语种)"""
    test_cases = [
        ("Hello, can you help me with math in English?", "en-US"),
        ("こんにちは、数学を教えてください", "ja-JP"),
        ("Guten Tag, kannst du mir bei der Mathematik helfen?", "de-DE"),
        ("Bonjour, comment vas-tu?", "fr-FR"),
        ("Hola! Como estas?", "es-ES"),
        ("你好，今天数学课有什么有趣的概念吗？", "zh-CN")
    ]
    
    for text, expected_lang in test_cases:
        t0 = time.time()
        payload = {
            "student_id": "TEST-AUDIT-AGENT",
            "voice_input_text": text,
            "selected_voice_key": "cute"
        }
        r = requests.post(f"{BASE_URL}/api/v1/voice/acoustic_chat", json=payload, timeout=8)
        latency_ms = (time.time() - t0) * 1000
        
        assert r.status_code == 200, f"接口返回非200状态码: {r.status_code}"
        data = r.json()
        
        # 1. 验证语种识别
        assert data["detected_language"] == expected_lang, f"语种匹配失败! 预期: {expected_lang}, 实际: {data['detected_language']}"
        
        # 2. 验证口语化精炼短句 (1-2 句口语短句，word count <= 30 或 字符数 <= 120)
        response_text = data["ai_voice_response_text"]
        words = response_text.split()
        assert len(words) <= 35 or len(response_text) <= 120, f"拒绝书面化啰嗦文字! 回答超出口语字数上限 ({len(response_text)}字符): '{response_text}'"
        
        # 3. 验证 24kHz Base64 MP3 音频 URL
        assert data["audio_data_url"] and data["audio_data_url"].startswith("data:audio"), "未生成有效 MP3 音频 Base64 数据"
        
        print(f"[Test 2 PASS] [{expected_lang}] 延迟: {latency_ms:.1f}ms | 问: '{text}' -> AI回答 ({len(response_text)}字符): '{response_text}'")

def test_03_barge_in_interrupt_speed():
    """验证全双工打断响应时间 < 200ms"""
    t0 = time.time()
    r = requests.post(f"{BASE_URL}/api/v1/voice/interrupt")
    latency_ms = (time.time() - t0) * 1000
    
    assert r.status_code == 200, "打断接口未返回 200 OK"
    assert latency_ms < 200, f"打断响应太慢，未达到全双工标准: {latency_ms:.1f}ms"
    print(f"[Test 3 PASS] 打断信号响应耗时: {latency_ms:.1f}ms (小于 200ms 门限)")

def test_04_static_code_inspection():
    """验证代码文件静态约束 (无死代码、无偷懒假数据)"""
    with open("backend/app/engine/voice_engine.py", "r", encoding="utf-8") as f:
        code = f.read()
    
    # 检查是否清除了假数据兜底
    assert "抱歉主帅，我刚才没有听清您的具体声音" not in code, "代码中仍然残存硬编码假回应!"
    # 检查是否引入了 1-2 句口语短句提示词
    assert "SHORT SPOKEN RESPONSES" in code or "1-2 spoken sentences" in code or "15-30 words" in code or "1-2句口语短句" in code, "缺少口语短句强约束系统提示词!"
    print("[Test 4 PASS] 静态代码防偷懒与合规审查 100% 通过！")

if __name__ == "__main__":
    print("==========================================================")
    print("【实时多语言语音智能体】 司法级独立验收测试套件 (Audit Ready)")
    print("==========================================================\n")
    try:
        test_01_api_health_check()
        test_02_multilingual_short_spoken_responses()
        test_03_barge_in_interrupt_speed()
        test_04_static_code_inspection()
        print("\n结论：所有司法级独立断言 100% 全部 PASS！合格交付！")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n验收失败断言: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n验收运行异常: {e}")
        sys.exit(1)
