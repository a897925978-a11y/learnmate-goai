# -*- coding: utf-8 -*-
"""
合合信息 TextIn 专业 OCR 试卷与手写体识别引擎 connector (textin_ocr.py)

安全防护规则：
1. 严禁在代码中硬编码真实 API Key / Secret！
2. 秘钥动态从本机的 .env 文件及环境变量 `TEXTIN_APP_ID` 和 `TEXTIN_SECRET_CODE` 加载。
"""

import os
import requests
import json
from typing import Dict, List, Any, Optional, Tuple
from pydantic import BaseModel


def get_textin_credentials() -> Tuple[str, str]:
    """
    安全读取本机环境变量中的 TextIn 凭据
    """
    app_id = os.environ.get("TEXTIN_APP_ID", "")
    secret_code = os.environ.get("TEXTIN_SECRET_CODE", "")
    return app_id, secret_code


class TextInOCRLineItem(BaseModel):
    text: str
    confidence: float
    position: List[int]  # [x1, y1, x2, y2, x3, y3, x4, y4]


class TextInOCRResult(BaseModel):
    status: str
    message: str
    raw_text: str
    lines: List[TextInOCRLineItem]
    is_live_api: bool


class TextInOCREngine:
    """
    合合信息 TextIn 专业 API 算控对接类
    """
    def __init__(self, api_url: str = "https://api.textin.com/ai/service/v2/recognize"):
        self.api_url = api_url

    def recognize_paper_image(self, image_bytes: Optional[bytes] = None) -> TextInOCRResult:
        app_id, secret_code = get_textin_credentials()

        # 校验秘钥保护
        if not app_id or not secret_code:
            return self._mock_fallback("未检测到本地 .env 中的 TEXTIN 凭据，已切换至安全的保护模式")

        if not image_bytes or len(image_bytes) < 10:
            return self._mock_fallback("未传入有效的试卷图片二进制流，已生成示范解析")

        # HTTP 请求头配置 (TextIn 官方安全鉴权规范)
        headers = {
            "x-ti-app-id": app_id,
            "x-ti-secret-code": secret_code,
            "Content-Type": "application/octet-stream"
        }

        try:
            res = requests.post(self.api_url, headers=headers, data=image_bytes, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if data.get("code") == 200:
                    result_item = data.get("result", {})
                    lines_data = result_item.get("lines", [])
                    
                    parsed_lines = []
                    raw_text_parts = []

                    for line in lines_data:
                        txt = line.get("text", "")
                        conf = float(line.get("score", 0.95))
                        pos = line.get("position", [0, 0, 0, 0, 0, 0, 0, 0])
                        parsed_lines.append(TextInOCRLineItem(text=txt, confidence=conf, position=pos))
                        raw_text_parts.append(txt)

                    return TextInOCRResult(
                        status="SUCCESS",
                        message="成功通过合合信息 TextIn API 识别试卷手写体与文本",
                        raw_text="\n".join(raw_text_parts),
                        lines=parsed_lines,
                        is_live_api=True
                    )

            # API 状态码非 200 降级兜底
            return self._mock_fallback(f"TextIn API 响应 [{res.status_code}]，触发容灾安全降级")

        except Exception as e:
            return self._mock_fallback(f"网络异常 [{str(e)}]，触发 TextIn 离线安全防护机制")

    def _mock_fallback(self, reason: str) -> TextInOCRResult:
        demo_lines = [
            TextInOCRLineItem(text="一、选择题：1. 2/3 + 1/4 = 3/7 (错)", confidence=0.98, position=[50, 120, 370, 120, 370, 205, 50, 205]),
            TextInOCRLineItem(text="二、解答题：2. 底 6cm 高 4cm 求面积 = 24cm² (漏乘 1/2)", confidence=0.95, position=[50, 240, 400, 240, 400, 330, 50, 330])
        ]
        return TextInOCRResult(
            status="SAFE_FALLBACK",
            message=f"🔒 保护模式机制激活：{reason}",
            raw_text="一、选择题：1. 2/3 + 1/4 = 3/7 (错)\n二、解答题：2. 底 6cm 高 4cm 求面积 = 24cm² (漏乘 1/2)",
            lines=demo_lines,
            is_live_api=False
        )


textin_engine = TextInOCREngine()
