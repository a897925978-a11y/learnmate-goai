# 🏛️ [通义千问 Qwen-Omni 实时语音 Agent] 顶级双向流式架构与重构开发文档

> **核心原则**：
> 1. **【模型方案】**：专为 **DashScope Qwen3.5-Omni (`qwen3.5-omni-flash`)** 原生打造！
> 2. **【协议架构】**：直接使用 **DashScope Realtime WebSocket Protocol (`wss://dashscope.aliyuncs.com/api-ws/v1/realtime`)**，做到 **16kHz PCM 输入 $\leftrightarrow$ 24kHz PCM 输出** 的双向原生 Audio-to-Audio 流！
> 3. **【零 UI 跳页】**：100% 维持原主界面，所有语音交互在 Header 状态指示灯与主聊天框内流式呈现！

---

## 一、 Qwen-Omni Realtime 双向流式架构拓扑

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│       DashScope Qwen3.5-Omni Realtime 原生音到音双向流式实时架构               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [前端主界面 (零全屏遮罩)]                                                      │
│  ├─ Web Audio API (AudioWorklet) ──> 采集 16kHz 16-bit PCM 原始音频流          │
│  ├─ 顶栏极简指示灯 & 主聊天框 ────< 接收 response.audio.delta 24kHz PCM 播音   │
│  └─ WebSocket Client (`ws://127.0.0.1:8000/ws/voice/omni_live`)                │
│                                │ ▲                                              │
│                                ▼ │ (全双工双向 WebSocket 代理)                  │
│  [Python 专用实时语音模块 (`qwen_omni_realtime_engine.py`)]                     │
│  ├─ 持有 DASHSCOPE_API_KEY 鉴权与 Session 状态                                  │
│  └─ WSS Bridge ──> 转发 input_audio_buffer.append / 接收 response.audio.delta │
│                                │ ▲                                              │
│                                ▼ │ (DashScope Realtime WSS Protocol)            │
│  [阿里云 DashScope Qwen-Omni 世界模型 Engine]                                   │
│  └─ Endpoint: wss://dashscope.aliyuncs.com/api-ws/v1/realtime                    │
│     * 模型 ID: qwen3.5-omni-flash / qwen3.5-omni-plus                           │
│     * 原生 Server VAD 感知、音到音 300ms 首包吐字、毫秒级打断 (Barge-in)          │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、 DashScope Qwen-Omni Realtime 协议事件规范

### 1. 会话初始化 (`session.update`)
后端模块与 DashScope 建连后，第一时间下发 Session 配置：
```json
{
  "type": "session.update",
  "session": {
    "modalities": ["text", "audio"],
    "instructions": "你是 Cartoon 萌宠伴学小狐狸【智小伴】。请用同种语言 1-2 句口语短句 (15-30字) 精准解答学生的问题！",
    "voice": "zhi_xiaoban",
    "input_audio_format": "pcm16",
    "output_audio_format": "pcm16",
    "turn_detection": {
      "type": "server_vad",
      "threshold": 0.5,
      "prefix_padding_ms": 300,
      "silence_duration_ms": 400
    }
  }
}
```

### 2. 前端 PCM 音频流实时追加 (`input_audio_buffer.append`)
前端每 20~100ms 抓取 16kHz PCM 音频数据，通过后端 Pipe 给 DashScope：
```json
{
  "type": "input_audio_buffer.append",
  "audio": "<Base64 encoded 16kHz PCM>"
}
```

### 3. Qwen-Omni 实时音频/文本回调流 (`response.audio.delta`)
 DashScope 边推理边实时吐包，后端原样推给前端播音：
```json
{
  "type": "response.audio.delta",
  "delta": "<Base64 encoded 24kHz PCM Audio>",
  "transcript": "实时生成的口语文本片段"
}
```

---

## 三、 零 UI 跳页原界面交互规范 (Zero-Jump Main UI)

1. **废除任何全屏弹窗**：`index.html` 维持原主界面显示，无 `#live-voice-call-overlay` 遮罩。
2. **顶栏波形指示**：开启语音后，顶栏仅显示 `🟢 Qwen-Omni 300ms 实时伴学中`。
3. **聊天框字幕**：
   - 麦克风收音字幕：`🎙️ [Qwen-Omni 听轨] 用户："..."`
   - AI 播音字幕：`🦊 [智小伴 · qwen3.5-omni] "..."`（边打字边播放 24kHz 音频）。

---

## 四、 写代码 Agent 重构任务清单

1. 新建 **`backend/app/engine/qwen_omni_realtime_engine.py`**：实现连接 DashScope `wss://dashscope.aliyuncs.com/api-ws/v1/realtime` 的专用实时语音 Bridge 模块。
2. 修改 **`backend/app/main.py`**：挂载 `@app.websocket("/ws/voice/omni_live")` 端点。
3. 修改 **`index.html`**：重构麦克风 PCM 采集与 Web Audio 队列播音，接入 `/ws/voice/omni_live`。

---

## 五、 司法级验收断言

- [ ] **模型确认**：日志与 WSS 消息确认使用的是 `qwen3.5-omni-flash` 原生 Realtime 协议。
- [ ] **界面维持**：开启语音后页面 100% 维持原主界面，零弹窗跳转。
- [ ] **延迟断言**：用户说话结束到听到 Qwen-Omni 第一声 PCM，**耗时 $<350\text{ms}$**。
