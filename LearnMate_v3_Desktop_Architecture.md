# 🖥️ 「智学伴 LearnMate AI Agent OS v3.0」原生桌面客户端全景开发方案

> **系统定位**：GOAI 世界人工智能开源大赛 · Boundless Agents (无界应用) 赛道参赛作品。  
> 将 **7 大 AI Agent 模块**（双重建档规划、Qwen-Omni/Gemini Live 实时语音对讲、错题 Vision OCR、物理遥测防作弊、心理熔断防护、Chroma 向量记忆、Tauri 2.0 桌面外壳）融为一体的**现象级原生 Windows 桌面操作系统级软件** (`LearnMate-Agent-OS_v3.0.exe`)。

---

## 一、 系统全景拓扑与 7 大 Agent 模块映射

```
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                 「智学伴 LearnMate AI Agent OS v3.0」全景原生桌面客户端                   │
├───────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                           │
│  [Windows 桌面标准软件外壳 (Tauri 2.0 Rust Shell)]                                        │
│  ├─ 界面视图: 100% 渲染高颜值 `index.html` (学情雷达、双端卡片、分镜预览、全场景控制台)   │
│  ├─ 悬浮学伴: 屏幕右下角 3D 极光动画萌宠 (Global Mascot Widget)                           │
│  └─ 硬件直连: 绕过浏览器 Autoplay 限制、全双工 16kHz PCM 音频采集与全局快捷键 (`Alt + V`)  │
│                                           │ ▲                                             │
│                                           ▼ │ (WebSocket / REST 双管道)                   │
│  [后端多 Agent 矩阵中枢 (Python FastAPI Engine Server - Port 8000)]                      │
│  ├── 1. 【个性化学习规划 Agent】: 双重建档 (初始50维+每日隐形微摸底) / 60:40 动态融合    │
│  ├── 2. 【实时多语言语音 Agent】: DashScope Qwen3.5-Omni / Gemini Live 全双工流式对讲   │
│  ├── 3. 【错题 Vision OCR 诊断 Agent】: 1秒图像特征提取与归因诊断 (知识点/错误类型)     │
│  ├── 4. 【4维物理遥测防作弊 Agent】: 首字响应/涂改频率/犹豫时长/看穿装懂/拦截装累博弈残差 │
│  ├── 5. 【心理危机熔断 Agent】: 极高危词硬阻断 & 400-161-9995 应急避险                    │
│  ├── 6. 【Chroma 0-Token 向量记忆 Agent】: 交互自动向量持久化与柱状/雷达学情生成           │
│  └── 7. 【Tauri 2.0 桌面外壳桥接模块】: 本地 WebSocket 服务与静态离线缓存                 │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 二、 桌面端 7 大 Agent 功能集成规范

### 1. 个性化学习规划 Agent (`planner_agent`)
- **功能**：首次双端建档，60:40 动态融合算法，1D 卡尔曼滤波，Sigmoid 阶段性熔断与 ZPD 动态调整。
- **UI 呈现**：主界面【学情画像控制台】与【艾宾浩斯 ZPD 学习路线图】。

### 2. 实时多语言语音对讲 Agent (`voice_live_agent`)
- **功能**：Qwen-Omni / Gemini Live 原生 Audio-to-Audio 双向流，支持中/英/日/德/法/西/俄/韩/阿数十种语言，$<300\text{ms}$ 首包发声与 $<20\text{ms}$ 打断。
- **UI 呈现**：主界面顶栏极光指示灯 + 主聊天框流式打字与 24kHz 音频播音，**零全屏弹窗跳转**。

### 3. 错题 Vision OCR 归因诊断 Agent (`ocr_agent`)
- **功能**：支持试卷拍立淘、错题图片解析、知识点锚定与归因分析。
- **UI 呈现**：【1秒 Vision OCR 试卷拍照】交互按钮与归因诊断卡片。

### 4. 4维无感物理遥测防作弊 Agent (`telemetry_agent`)
- **功能**：首字响应 (First-Key)、涂改频率 (Backspace)、犹豫时长 (Option Hover) 4维遥测，“看穿装懂”、“拦截装累”博弈残差判定。
- **UI 呈现**：【4维无感物理遥测控制台】与实时残差仪表盘。

### 5. 心理危机熔断 Agent (`crisis_agent`)
- **功能**：检测自杀/自残/跳楼等高危词，100% 阻断对话，弹出国家救援热线 400-161-9995。
- **UI 呈现**：全屏红色高危保护 Modal。

### 6. Chroma 0-Token 向量记忆 Agent (`vector_agent`)
- **功能**：所有语音、打字、错题诊断交互自动向量化入库，生成多维雷达图与周报。
- **UI 呈现**：【Chart.js 学情雷达图】与向量记忆库视图。

### 7. Tauri 2.0 桌面外壳封装 (`desktop_shell`)
- **功能**：打包为独立 Windows `.exe` 安装包，提供桌面右下角悬浮学伴、全局快捷键与后台常驻。

---

## 三、 桌面软件构建与打包标准流程

1. **环境准备**：
   - Rust 1.75+ (`rustup default stable`)
   - Node.js 18+
2. **初始化项目**：
   ```bash
   npx @tauri-apps/cli init
   ```
3. **本地调试运行**：
   ```bash
   npx tauri dev
   ```
4. **编译打出 Windows `.exe` 安装包**：
   ```bash
   npx tauri build
   ```
   产物输出路径：`src-tauri/target/release/bundle/nsis/LearnMate-Agent-OS_3.0.0_x64-setup.exe`。
