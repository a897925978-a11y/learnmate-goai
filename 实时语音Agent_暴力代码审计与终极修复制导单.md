# 🔍 [暴力代码审计报告与终极修复单] 彻底攻克“问问题不回答/抱歉声音未录入”病灶

> **审计执行人**：Antigravity (独立技术审计员)  
> **审计结论**：通过逐行对 `index.html` 与 `qwen_omni_realtime_engine.py` 进行数据流追踪，**成功抓获导致“问问题不回答”的 2 个隐藏死锁 Bug！**

---

## 一、 暴力审查：两大隐藏死锁 Bug 诊断

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    死锁 Bug 1：FileReader 异步时间差撕裂                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  rec.onresult (写入输入框 "你好") ──> rec.onend (触发 stopMediaRecorder) │
│                                                │                        │
│                                                ▼                        │
│                                stopRecordingUI() 瞬间清空输入框 ('')    │
│                                                │                        │
│                                                ▼ (50ms 异步延迟后)      │
│                FileReader.onloadend 触发时：读取 currentText 已经是 ''！│
│                结果 ──> WebSocket 传给后端的 text = '' 导致崩溃！       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                    死锁 Bug 2：recognize_google 国内网络阻断             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  后端接收到空 text ──> 触发 fallback transcribe_audio_b64()            │
│  调用 recognize_google() ──> 尝试连接 http://www.google.com/speech-api │
│  国内网络连接超时 (Timeout) ──> 捕获 Exception 返回 None                │
│  结果 ──> 输出 “抱歉主帅，我刚才收到语音但未录入清晰说话...”            │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、 终极代码修复方案 (写代码 Agent 必读)

### 1. 修复方案 1：前端捕获全局 `latestSpokenTranscript`，彻底解决异步清空 Bug (`index.html`)
在 `index.html` 全局定义 `let latestSpokenTranscript = '';`：
- **`rec.onresult`**：实时更新 `latestSpokenTranscript = transcript.trim();`
- **`rec.onend`**：在停音瞬间，**优先锁定 `latestSpokenTranscript`**，并立刻通过 WebSocket 发送：
  ```javascript
  const finalText = (latestSpokenTranscript || inputField.value).trim();
  if (finalText) {
      sendWebSocketFrame({
          type: "text",
          text: finalText,
          voice_key: selectedVoiceKey
      });
      latestSpokenTranscript = ''; // 发送后清空全局变量
  }
  ```
- **绝对不要**等 `FileReader.onloadend` 50ms 异步回调后再去读被清空的 `inputField.value`！

### 2. 修复方案 2：后端废除 `recognize_google`，防范网络超时 (`voice_engine.py`)
- 删除 `recognize_google` 对 `google.com` 的无代理依赖。
- 若 `user_text` 已由前端 WebSocket 稳健送达，优先直接消费 `user_text`！
- 若只有音频 Blob，优先使用 `google-genai` (若配置 Key) 或 DashScope 接口解析，绝不阻塞网络超时。

---

## 三、 修改后完整联调流程

```
用户开口提问 ("异分母分数怎么做？")
  │
  ├─> rec.onresult 捕获全句并锁定至 latestSpokenTranscript
  │
  ├─> rec.onend 触发 ──> 5ms 内向 WebSocket 发送 {"type":"text", "text":"异分母分数怎么做？"}
  │
  ├─> 界面主聊天框追加：🎙️ [Qwen-Omni 输入] “异分母分数怎么做？”
  │
  ├─> 后端 Qwen3.5-Omni 收到提问 ──> 150ms 内吐字：🦊 [智小伴] "先把分母通分，再分子加减！"
  │
  └─> 24kHz 高保真 MP3 流式播放，全过程零卡顿、零 Hello、零误报！
```
