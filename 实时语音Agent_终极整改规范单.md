# 🛠️ [终极整改开发工单] 实时语音 Agent (Gemini Live 电话对讲模式) 修复规范

> **⚠️ 使用说明**：请直接将本工单无删减复制发给负责写代码的 Agent (Kimi / Worker Agent)。要求其按照本规范对 `index.html` 与后端进行针对性整改。

---

## 一、 体验病灶诊断报告 (为何刚才“不像电话、问问题不回答”？)

通过分析你测试时的抓包与截图，定位到 3 个严重逻辑冲突：

1. **混淆了“离线语音条 HTTP POST”与“实时 WebSocket 流”**：
   - 开启实时通话后，前端居然还在调用 `sendChatMessage()` 触发离线 HTTP POST `/api/v1/voice/acoustic_chat`！
   - 导致生成的不是电话式的实时字幕，而是带播放按钮的“微信语音条”。
2. **麦克风转录断流，导致 input_text 变空**：
   - 录音停止时，`inputField.value` 还没来得及填充，就被清空发送了，导致后端收到空文字，触发了 `(声音未检测到)`。
3. **输入框文字未自动清除流式发往 WebSocket**：
   - 打字框里的文字没有在说话/断句时自动捕获发给 WebSocket，导致用户打的字卡在输入框里。

---

## 二、 3 大核心整改任务 (代码 Agent 执行规范)

### 任务 1：实时通话模式下，100% 走 WebSocket 流，废除 HTTP POST (`index.html`)
- 在开启 `isContinuousCallActive = true` 实时通话状态时：
  - **彻底禁用** `sendChatMessage()` 的 HTTP POST 提交！
  - 当 VAD / Web Speech API 识别到用户说话结束时，**自动通过 WebSocket 发送数据**：
    ```javascript
    sendWebSocketFrame({
        type: "text",
        text: userTranscriptText,
        voice_key: selectedVoiceKey
    });
    ```

### 任务 2：聊天记录实时流式追加 & 清空输入框（供 Chroma 向量库入库）
- **用户说话完结瞬间**：
  - 自动向主聊天框 `#chat-box` 追加绿色气泡：
    `🎙️ [Gemini Live] “用户口述的真实提问”`
  - 自动清空 `#chat-input-field` 输入框，防止文字卡在框里。
- **AI 收到回答瞬间**：
  - 自动向 `#chat-box` 追加紫色气泡：
    `🦊 [智小伴 · Gemini Live] AI 实时回答`
  - 触发 Web Audio 流式播放 24kHz 音频，并将对话自动存入 ChromaDB 向量记忆库！

### 3. 任务 3：像电话一样的全自动连续听讲 (Hands-Free Phone Experience)
- AI 播音结束时（收到 `stream_end`），前端在 300ms 内自动重新唤醒麦克风倾听；
- 用户中途开口时，前端瞬间调用 `interruptAISpeech()` 并发送 `{"type": "interrupt"}`，20ms 内切断 AI 发声。
- 全程**零手动点击**，完美媲美 Gemini Live / 真实电话体验！

---

## 三、 整改自检与交付验证

代码 Agent 提交修改后，必须自行确认：
1. 打开实时通话后，说话是否**像打电话一样自动在主聊天框吐出字幕**？
2. `#chat-input-field` 输入框里的文字是否在说话后自动清空并提交？
3. 对话气泡是否实时生成，且不再出现“微信语音条”或“(声音未检测到)”？
