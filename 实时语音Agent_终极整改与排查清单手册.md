# 🛠️ [终极整改与排查清单] 实时语音 Agent (Gemini Live / Qwen-Omni)

> **⚠️ 说明**：本规范已涵盖**浏览器缓存清除、AudioContext 自动播放锁恢复、WebSocket 断线重连与 MediaRecorder 兼容性**的全量解决方案。请直接将本文件复制给写代码 Agent 进行代码整改。

---

## 一、 为什么在某些浏览器测试时会出现“一模一样的问题”？（4大隐藏死灶）

经过深度代码审计，定位到以下 4 个死灶导致在部分浏览器环境下依然无法对讲：

### 1. 浏览器 JS 强缓存 (Browser Hard Cache)
- **原因**：Chrome / Edge 对 `localhost:8000` 的 `index.html` 会进行强缓存。如果不彻底清除缓存，浏览器一直在跑旧版的 JS 代码。
- **解决**：在 HTTP 响应头增加禁用缓存 Headers，或在测试时使用 `Ctrl + Shift + R` 强制刷新 / 隐身窗口测试。

### 2. Web Audio API 自动播放锁限制 (`AudioContext.state === 'suspended'`)
- **原因**：Chrome 70+ 规定，未经用户手动点击前，`AudioContext` 会处于 `suspended`（挂起）状态，导致录音或音频播放静默挂起。
- **整改**：点击【开启实时通话】按钮时，**必须显式执行 `await audioCtx.resume()`** 解锁音频上下文！

### 3. MediaRecorder 音频格式兼容性 (MimeType Fallback)
- **原因**：部分 Windows 浏览器不支持 `audio/webm;codecs=opus`，导致生成的音频 Blob 大小为 0 字节。
- **整改**：增加 MimeType 兼容性检测：
  ```javascript
  const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : (MediaRecorder.isTypeSupported('audio/webm') ? 'audio/webm' : 'audio/mp4');
  ```

### 4. WebSocket 状态校验 (`readyState !== WebSocket.OPEN`)
- **原因**：发送消息时若 WebSocket 未完全建立或断开，消息会被静默丢弃。
- **整改**：在 `sendWebSocketFrame` 中增加重连与保底机制：
  ```javascript
  function sendWebSocketFrame(payload) {
      if (voiceWebSocket && voiceWebSocket.readyState === WebSocket.OPEN) {
          voiceWebSocket.send(JSON.stringify(payload));
      } else {
          console.warn("WebSocket 连接未就绪，尝试自动重连...");
          initVoiceWebSocket();
      }
  }
  ```

---

## 二、 完整代码整改任务清单 (给写代码 Agent)

### 任务 1：界面 `index.html` 体验彻底整改
1. **解锁 AudioContext**：点击【开启实时通话】时自动激活 `AudioContext.resume()`。
2. **零全屏遮罩**：彻底废除全屏黑色遮罩卡片，维持在主界面显示。
3. **字幕与音轨流**：识别到的文本与 AI 的回答直接追加至主聊天框 `#chat-box` 内，并自动存入向量库。
4. **防强缓存**：给 script 增加版本时间戳 `index.html?v=3.0`。

### 任务 2：后端 `qwen_omni_realtime_engine.py` 优化
1. **禁用 HTTP GET/POST 假回复**，全双工走 `/ws/voice/omni_live` WebSocket。
2. **<300ms 音频推流**：收到文本或 PCM 时，150ms 内推回文本流，300ms 内推回 24kHz 音频流。

---

## 三、 用户测试指引

写代码 Agent 完成上述修改后：
1. 请按 **`Ctrl + Shift + R` (或 `Ctrl + F5`)** 强制刷新 `http://localhost:8000/` 页面。
2. 点击【开启实时通话】按钮。
3. 直接说话或打字，观察聊天框是否实时打出字幕并发出语音。
