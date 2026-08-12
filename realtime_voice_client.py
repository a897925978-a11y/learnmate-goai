# -*- coding: utf-8 -*-
"""
智学伴 LearnMate — 真·实时语音客户端 (DashScope Qwen-Omni Realtime)

100% 原生 Audio-to-Audio 流式通话引擎：
- 麦克风 PCM 帧直推 WebSocket → Qwen-Omni 原生处理 → PCM 帧流式回传
- 零 ASR、零 TTS、零中间文字转换、零磁盘 IO
- 服务端智能语义 VAD + 全双工打断 (Barge-in)
- 目标首包延迟 < 500ms
"""

import os
import sys
import base64
import queue
import threading
import time
import traceback
from typing import Callable, Optional

# 确保项目根目录在 sys.path 中以便读取 .env
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# 加载 .env 环境变量
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    pass


class RealtimeVoiceClient:
    """
    DashScope Qwen-Omni Realtime WebSocket 语音客户端

    音频直进直出，零中间层：
    - 输入: PCM 16kHz 16bit Mono
    - 输出: PCM 24kHz 16bit Mono
    - 服务端 VAD 自动检测说话起止
    - 原生全双工打断 (Barge-in)
    """

    # 输入音频格式
    INPUT_SAMPLE_RATE = 16000
    INPUT_CHANNELS = 1
    INPUT_SAMPLE_WIDTH = 2  # 16-bit

    # 输出音频格式
    OUTPUT_SAMPLE_RATE = 24000
    OUTPUT_CHANNELS = 1
    OUTPUT_SAMPLE_WIDTH = 2  # 16-bit

    def __init__(
        self,
        on_ai_audio: Optional[Callable[[bytes], None]] = None,
        on_ai_text: Optional[Callable[[str], None]] = None,
        on_ai_text_done: Optional[Callable[[str], None]] = None,
        on_user_transcript: Optional[Callable[[str], None]] = None,
        on_state_change: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[str], None]] = None,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化实时语音客户端

        Args:
            on_ai_audio: AI 音频帧到达回调 — callback(pcm_bytes: bytes)
            on_ai_text: AI 文字流式输出回调 — callback(text_delta: str)
            on_ai_text_done: AI 完整文字输出回调 — callback(full_text: str)
            on_user_transcript: 用户语音转文字回调 — callback(transcript: str)
            on_state_change: 状态变化回调 — callback(state: str)
                states: "connecting", "connected", "listening", "ai_speaking", "disconnected", "error"
            on_error: 错误回调 — callback(error_msg: str)
            system_prompt: 自定义 System Prompt
        """
        self.on_ai_audio = on_ai_audio or (lambda x: None)
        self.on_ai_text = on_ai_text or (lambda x: None)
        self.on_ai_text_done = on_ai_text_done or (lambda x: None)
        self.on_user_transcript = on_user_transcript or (lambda x: None)
        self.on_state_change = on_state_change or (lambda x: None)
        self.on_error = on_error or (lambda x: None)

        self._system_prompt = system_prompt or self._default_system_prompt()
        self._conversation = None
        self._connected = False
        self._ai_speaking = False
        self._accumulated_ai_text = ""
        self._accumulated_user_text = ""

        # DashScope 凭据
        self._api_key = os.environ.get("DASHSCOPE_API_KEY", "")
        self._workspace_id = os.environ.get("DASHSCOPE_WORKSPACE_ID", "")
        self._base_url = os.environ.get("DASHSCOPE_BASE_URL", "")

        # 构建 Realtime WebSocket URL
        if self._workspace_id:
            self._ws_url = f"wss://{self._workspace_id}.cn-beijing.maas.aliyuncs.com/api-ws/v1/realtime"
        else:
            self._ws_url = ""

        self._model = "qwen3.5-omni-flash-realtime"

    @staticmethod
    def _default_system_prompt():
        return (
            "你是「智小伴」，一个温暖、聪明、有趣的 AI 学习伙伴，由智学伴 LearnMate 团队打造。\n"
            "你正在通过实时语音电话和学生对话。\n\n"
            "核心规则：\n"
            "1. 用和学生相同的语言回答（中文问就用中文答，英文问就用英文答）。\n"
            "2. 回答简短有力，像真正的朋友打电话一样自然，每次 1-3 句话。\n"
            "3. 对学术问题要专业准确，但表达要口语化、亲切。\n"
            "4. 适当使用语气词让对话更自然（嗯、哦、呀、呢）。\n"
            "5. 如果学生问了你不确定的问题，诚实说不确定，不要编造。\n"
            "6. 你有幽默感，会鼓励学生，但不会过分夸张。"
        )

    def connect(self) -> bool:
        """
        建立 WebSocket 连接到 DashScope Qwen-Omni Realtime API

        Returns:
            True if connected successfully, False otherwise
        """
        if self._connected:
            return True

        if not self._api_key:
            self.on_error("未配置 DASHSCOPE_API_KEY，无法建立实时语音连接")
            return False

        if not self._ws_url:
            self.on_error("未配置 DASHSCOPE_WORKSPACE_ID，无法构建 WebSocket URL")
            return False

        self.on_state_change("connecting")

        try:
            from dashscope.audio.qwen_omni import OmniRealtimeConversation, OmniRealtimeCallback
            from dashscope.audio.qwen_omni.omni_realtime import MultiModality

            # 创建回调处理器 — 使用闭包绑定 self
            client_ref = self

            class _RealtimeCallback(OmniRealtimeCallback):
                """DashScope Realtime 回调处理器"""

                def on_open(self):
                    """WebSocket 连接打开"""
                    print("[RealtimeVoiceClient] WebSocket opened")

                def on_close(self, close_status_code, close_msg):
                    """WebSocket 连接关闭"""
                    print(f"[RealtimeVoiceClient] WebSocket closed: {close_status_code} {close_msg}")
                    client_ref._connected = False
                    client_ref.on_state_change("disconnected")

                def on_event(self, message):
                    """处理所有服务端事件 — SDK 可能传入 dict 或 JSON str"""
                    try:
                        if isinstance(message, dict):
                            data = message
                        elif isinstance(message, str):
                            import json as _json
                            data = _json.loads(message)
                        else:
                            print(f"[RealtimeVoiceClient] Unknown message type: {type(message)}")
                            return
                        event_type = data.get("type", "unknown")
                        client_ref._handle_event(event_type, data)
                    except Exception as e:
                        print(f"[RealtimeVoiceClient] Callback error: {e}")
                        traceback.print_exc()

            callback = _RealtimeCallback()

            # 创建并连接 OmniRealtimeConversation
            self._conversation = OmniRealtimeConversation(
                model=self._model,
                callback=callback,
                url=self._ws_url,
            )

            self._conversation.connect()

            # 配置会话参数
            self._conversation.update_session(
                # 开启服务端 VAD — 自动检测说话起止
                enable_turn_detection=True,
                # 输出模态: 同时输出音频和文字 (使用 SDK 枚举)
                output_modalities=[MultiModality.AUDIO, MultiModality.TEXT],
                # 语音音色 (Tina = qwen3.5-omni-flash-realtime 默认音色)
                voice="Tina",
                # 注入 System Prompt
                instructions=self._system_prompt,
            )

            self._connected = True
            self._ai_speaking = False
            self.on_state_change("connected")
            print(f"[RealtimeVoiceClient] [OK] Connected to {self._ws_url}")
            return True

        except Exception as e:
            err_msg = f"实时语音连接失败: {e}"
            print(f"[RealtimeVoiceClient] [FAIL] {err_msg}")
            traceback.print_exc()
            self.on_error(err_msg)
            self.on_state_change("error")
            return False

    def _handle_event(self, event_type: str, data: dict):
        """
        统一处理 DashScope Realtime 服务端事件

        事件类型参考:
        - session.created: 会话创建成功
        - session.updated: 会话配置更新
        - input_audio_buffer.speech_started: 用户开始说话 (VAD)
        - input_audio_buffer.speech_stopped: 用户停止说话 (VAD)
        - response.created: AI 开始生成回复
        - response.audio.delta: AI 音频帧 (PCM Base64)
        - response.audio.done: AI 音频输出完成
        - response.audio_transcript.delta: AI 语音对应的文字转录增量
        - response.audio_transcript.done: AI 文字转录完成
        - response.text.delta: AI 纯文字增量
        - response.text.done: AI 纯文字完成
        - input_audio_buffer.committed: 音频缓冲已提交
        - conversation.item.input_audio_transcription.completed: 用户语音转文字完成
        - response.done: AI 回复完全结束
        - error: 错误
        """

        if event_type == "session.created":
            print(f"[RealtimeVoiceClient] Session created: {data.get('session', {}).get('id', 'unknown')}")
            self.on_state_change("listening")

        elif event_type == "session.updated":
            print(f"[RealtimeVoiceClient] Session updated")

        elif event_type == "input_audio_buffer.speech_started":
            # 用户开始说话 — 如果 AI 正在说话，触发打断
            if self._ai_speaking:
                self._ai_speaking = False
                # 服务端会自动停止 AI 音频输出
            self.on_state_change("listening")

        elif event_type == "input_audio_buffer.speech_stopped":
            # 用户停止说话 — 服务端 VAD 检测到静音
            pass

        elif event_type == "response.created":
            # AI 开始生成回复
            self._ai_speaking = True
            self._accumulated_ai_text = ""
            self.on_state_change("ai_speaking")

        elif event_type == "response.audio.delta":
            # 🔑 核心: AI 音频帧到达 — PCM Base64 编码
            audio_b64 = data.get("delta", "") or data.get("audio", "")
            if audio_b64:
                try:
                    pcm_bytes = base64.b64decode(audio_b64)
                    self.on_ai_audio(pcm_bytes)
                except Exception as e:
                    print(f"[RealtimeVoiceClient] Audio decode error: {e}")

        elif event_type == "response.audio.done":
            # AI 音频输出完成
            self._ai_speaking = False

        elif event_type == "response.audio_transcript.delta":
            # AI 语音对应文字增量
            text_delta = data.get("delta", "")
            if text_delta:
                self._accumulated_ai_text += text_delta
                self.on_ai_text(text_delta)

        elif event_type == "response.audio_transcript.done":
            # AI 文字完成
            full_text = data.get("transcript", "") or self._accumulated_ai_text
            if full_text:
                self.on_ai_text_done(full_text)

        elif event_type == "response.text.delta":
            text_delta = data.get("delta", "")
            if text_delta:
                self._accumulated_ai_text += text_delta
                self.on_ai_text(text_delta)

        elif event_type == "response.text.done":
            full_text = data.get("text", "") or self._accumulated_ai_text
            if full_text:
                self.on_ai_text_done(full_text)

        elif event_type == "conversation.item.input_audio_transcription.completed":
            # 用户语音转文字完成
            transcript = data.get("transcript", "")
            if transcript:
                self.on_user_transcript(transcript)

        elif event_type == "response.done":
            # AI 回复完全结束
            self._ai_speaking = False
            self.on_state_change("listening")

        elif event_type == "error":
            err_msg = data.get("error", {}).get("message", str(data))
            print(f"[RealtimeVoiceClient] Server error: {err_msg}")
            self.on_error(f"服务端错误: {err_msg}")

        else:
            # 未知事件 — 调试输出
            pass

    def send_audio_frame(self, pcm_bytes: bytes):
        """
        实时推送一帧麦克风 PCM 音频到服务端

        SDK 的 append_audio() 需要 Base64 编码的字符串。

        Args:
            pcm_bytes: 16kHz 16bit Mono PCM 原始字节
        """
        if not self._connected or not self._conversation:
            return

        try:
            audio_b64 = base64.b64encode(pcm_bytes).decode('ascii')
            self._conversation.append_audio(audio_b64)
        except Exception as e:
            print(f"[RealtimeVoiceClient] Send audio error: {e}")

    def interrupt(self):
        """打断当前 AI 语音输出"""
        if self._ai_speaking and self._connected and self._conversation:
            try:
                self._conversation.cancel_response()
                self._ai_speaking = False
            except Exception:
                pass

    def disconnect(self):
        """断开 WebSocket 连接"""
        self._connected = False
        self._ai_speaking = False

        if self._conversation:
            try:
                self._conversation.close()
            except Exception:
                pass
            self._conversation = None

        self.on_state_change("disconnected")
        print("[RealtimeVoiceClient] Disconnected")

    @property
    def is_connected(self) -> bool:
        return self._connected

    @property
    def is_ai_speaking(self) -> bool:
        return self._ai_speaking


class RealtimeAudioPlayer:
    """
    PCM 实时音频播放器

    使用 PyAudio output stream 低延迟播放 AI 返回的 PCM 帧。
    维护帧缓冲队列，独立线程持续消费。
    """

    def __init__(self, sample_rate: int = 24000, channels: int = 1):
        self._sample_rate = sample_rate
        self._channels = channels
        self._queue = queue.Queue(maxsize=500)  # 帧缓冲队列
        self._running = False
        self._thread = None
        self._pa = None
        self._stream = None

    def start(self):
        """启动播放器线程"""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()

    def _play_loop(self):
        """播放线程主循环"""
        try:
            import pyaudio
            self._pa = pyaudio.PyAudio()
            self._stream = self._pa.open(
                format=pyaudio.paInt16,
                channels=self._channels,
                rate=self._sample_rate,
                output=True,
                frames_per_buffer=1200,  # ~50ms @24kHz
            )

            while self._running:
                try:
                    pcm_data = self._queue.get(timeout=0.1)
                    if pcm_data is None:
                        continue
                    self._stream.write(pcm_data)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"[AudioPlayer] Playback error: {e}")
                    time.sleep(0.01)

        except Exception as e:
            print(f"[AudioPlayer] Init error: {e}")
        finally:
            self._cleanup_stream()

    def enqueue(self, pcm_bytes: bytes):
        """将 AI 音频帧放入播放队列"""
        if not self._running:
            return
        try:
            self._queue.put_nowait(pcm_bytes)
        except queue.Full:
            # 队列满了，丢弃最旧的帧
            try:
                self._queue.get_nowait()
                self._queue.put_nowait(pcm_bytes)
            except:
                pass

    def clear(self):
        """清空播放队列 — 用于打断"""
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
            except:
                break

    def stop(self):
        """停止播放器"""
        self._running = False
        self.clear()
        if self._thread:
            self._thread.join(timeout=2)
        self._cleanup_stream()

    def _cleanup_stream(self):
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except:
                pass
            self._stream = None
        if self._pa:
            try:
                self._pa.terminate()
            except:
                pass
            self._pa = None


# ============================================================
# 独立测试入口
# ============================================================
if __name__ == "__main__":
    import struct

    print("=" * 60)
    print("智学伴 RealtimeVoiceClient 独立测试")
    print("=" * 60)

    player = RealtimeAudioPlayer(sample_rate=24000, channels=1)
    received_audio = False
    received_text = False
    full_ai_text = ""

    def on_audio(pcm_bytes):
        global received_audio
        received_audio = True
        player.enqueue(pcm_bytes)

    def on_text(delta):
        print(delta, end="", flush=True)

    def on_text_done(text):
        global received_text, full_ai_text
        received_text = True
        full_ai_text = text
        print(f"\n[AI 完整回复] {text}")

    def on_user_transcript(text):
        print(f"\n[用户说] {text}")

    def on_state(state):
        print(f"\n[状态] {state}")

    def on_error(msg):
        print(f"\n[错误] {msg}")

    client = RealtimeVoiceClient(
        on_ai_audio=on_audio,
        on_ai_text=on_text,
        on_ai_text_done=on_text_done,
        on_user_transcript=on_user_transcript,
        on_state_change=on_state,
        on_error=on_error,
    )

    if not client.connect():
        print("连接失败，退出")
        sys.exit(1)

    player.start()

    # 用麦克风采集并推流
    try:
        import pyaudio

        pa = pyaudio.PyAudio()
        mic_stream = pa.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=1600,  # 100ms @16kHz
        )

        print("\n🎙️ 麦克风已开启，请说话... (Ctrl+C 退出)")

        while True:
            pcm_data = mic_stream.read(1600, exception_on_overflow=False)
            client.send_audio_frame(pcm_data)

    except KeyboardInterrupt:
        print("\n\n用户中断")
    finally:
        mic_stream.stop_stream()
        mic_stream.close()
        pa.terminate()
        client.disconnect()
        player.stop()

        print("\n" + "=" * 60)
        print(f"测试结果: 收到AI音频={received_audio}, 收到AI文字={received_text}")
        if full_ai_text:
            print(f"AI 回复: {full_ai_text}")
        print("=" * 60)
