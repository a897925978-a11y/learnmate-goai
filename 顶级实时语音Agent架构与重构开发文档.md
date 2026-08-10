# 🏛️ [顶级架构文档]  Gemini Multimodal Live 双向原生流式实时语音 Agent 重构方案

> **核心原则**：
> 1. **【零 UI 跳页，维持原界面】**：彻底废除全屏弹窗 (Modal Overlay)，所有语音交互直接在主界面顶栏与聊天框内完成！
> 2. **【不是问答机器人，是实时语音 Agent】**：基于 **Gemini Multimodal Live API (BidiGenerateContent)** 打造原生音到音 (Audio-to-Audio) 双向流式架构，放弃传统 STT $\to$ LLM $\to$ TTS 串行级联高延时模型！

---

## 一、 为什么之前的版本体验糟糕？（病灶对照）

| 体验病灶 | 旧版做法 (痛点) | 顶级 Gemini Live 架构重构方案 |
|:---|:---|:---|
| **UI 交互** | 强制弹出一个全屏黑色弹窗 (`live-voice-call-overlay`)，打断了主界面体验 | **100% 维持在主界面**，顶栏显示极简实时音频波动，字幕直接打在主聊天框 |
| **实时性** | 假实时！按住录音 $\to$ 等待上传 $\to$ 耗时 3~5 秒返回静态 JSON | **真双向流式 (Bi-directional Streaming)**！PCM 字节流毫秒级上传，首包发声 $< 300\text{ms}$ |
| **打断能力** | 伪打断，依赖客户端发送静态 `POST /interrupt` | **原生 Server VAD 打断**！Gemini 模型原生感应用户说话，20ms 内自动停止推流 |
| **智商与语言** | 依赖简单文本转录，丢弃了语速、情绪、停顿 | **原生音到音 (Audio-to-Audio)**！直接处理 16kHz PCM 原音，保留语气与情感，支持全球数十种语言 |

---

## 二、 顶级 Gemini Multimodal Live API 架构拓扑

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              Gemini 2.5 Multimodal Live API 原生音到音双向流式架构             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [前端主界面 (零跳页)]                                                          │
│  ├─ Web Audio API (AudioWorklet) ──> 采集 16kHz 16-bit PCM 原始音频流          │
│  ├─ 顶栏极简波形 & 主聊天框 ────< 实时接收 24kHz 24-bit PCM 播音 & 字幕         │
│  └─ WebSocket Client (`ws://127.0.0.1:8000/ws/voice/live`)                      │
│                                │ ▲                                              │
│                                ▼ │ (全双工双向 WebSocket 代理)                  │
│  [Python FastAPI 后端安全代理中枢 (Engine Proxy)]                               │
│  ├─ 管理 Session 密钥与 Gemini Live WSS 连接                                   │
│  └─ WebSocket Bridge ──> 转发 realtime_input / 接收 server_content            │
│                                │ ▲                                              │
│                                ▼ │ (WSS 双向流)                                  │
│  [Google Gemini Multimodal Live API (Cloud Engine)]                             │
│  └─ Endpoint: wss://generativelanguage.googleapis.com/.../BidiGenerateContent   │
│     * 原生感知语音情绪、抑扬顿挫、多语言与 VAD 实时打断                         │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 三、 零 UI 跳页：原界面交互规范 (Zero-Jump Main UI Design)

### 1. 废除全屏弹窗 (`index.html`)
- 彻底移除 `#live-voice-call-overlay` 遮罩层。
- 无论用户是在做题、看学情雷达，还是在聊天，点击顶栏/底栏麦克风图标后，**界面保持完全不动**。

### 2. 原界面两大视觉元素：
- **顶栏声音状态指示灯 (Header Live Pill)**：主界面顶栏显示一个小巧的极光光晕 `🟢 实时语音伴学中 (Gemini Live 300ms)`。
- **主聊天框字幕流 (Main Chat Transcript Stream)**：
  - 用户说话时，主聊天框实时出现 `🎙️ [实时听轨] 用户："..."`；
  - 智小伴回答时，主聊天框实时打字 `🦊 [智小伴] "..."`，同时网页扬声器通过 Web Audio API 流式播放 24kHz 真人音频。

---

## 四、 核心技术实现细节

### 1. 前端 PCM 采集与播放 (`AudioWorklet`)
- **音频采集**：不使用 WebM/MediaRecorder，直接使用 `AudioContext.createScriptProcessor` 或 `AudioWorkletNode` 提取 **16000Hz 16-bit Mono PCM 字节流**。
- **Base64 编码分包**：每 100ms 将 PCM 字节转换为 Base64，通过 WebSocket 结构发送：
  ```json
  {
    "realtime_input": {
      "media_chunks": [
        {
          "mime_type": "audio/pcm",
          "data": "<Base64 PCM Chunks>"
        }
      ]
    }
  }
  ```
- **音频流式播放**：使用 Web Audio API `AudioBufferSourceNode` 队列，收到 24kHz PCM Base64 时自动无缝拼接播放。

### 2. 后端 WebSocket 代理 (`backend/app/main.py`)
- 提供 `/ws/voice/live` 双向 WebSocket 端点：
  ```python
  @app.websocket("/ws/voice/live")
  async def websocket_voice_live_endpoint(websocket: WebSocket):
      await websocket.accept()
      # 连接 Gemini Live API WSS 端点
      # 双向 asyncio.gather 建立桥接转发
  ```

### 3. 原生打断 (Barge-in) 机制
- 当用户开口说话时，Gemini Live API 内部 Server VAD 自动检测到声音，并在 WSS 返回 `{"server_event": "interrupted"}`。
- 前端收到后，瞬间调用 `audioCtx.suspend()` 并清空当前播放队列（耗时 $<50\text{ms}$）。

---

## 五、 代码重构指令与验收标准

### 写代码 Agent 重构任务
1. **`index.html`**：删掉 `live-voice-call-overlay` 全屏弹窗；重构麦克风触发逻辑，维持主界面显示；实现 PCM AudioWorklet 采集与流式播音。
2. **`backend/app/engine/voice_live_engine.py`**：新增 Gemini Live API WSS 代理与链路管理。
3. **`backend/app/main.py`**：挂载 `/ws/voice/live` WebSocket 端点。

### 司法级验收断言
- [ ] **UI 检查**：点击开启语音后，网页**零页面跳转/零全屏弹窗**，完全维持在原主界面。
- [ ] **流式延迟**：用户说话结束到听见第一声 Gemini 音频，**耗时 $<400\text{ms}$**。
- [ ] **原生打断**：在 AI 发声时说话，音频在 **50ms 内瞬间中断**。
