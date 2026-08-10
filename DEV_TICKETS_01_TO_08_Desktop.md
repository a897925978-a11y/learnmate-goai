# 🎫 「智学伴 LearnMate v3.0」8大模块桌面软件完整开发任务单手册

> **全套工单索引**：本手册包含将整套「智学伴 LearnMate v3.0」打造为 **Windows 标准桌面软件 (.exe)** 所需的全部 8 个模块开发工单。

---

## 📋 工单总览表

| 工单编号 | 模块名称 | 核心职责 | 依赖项 | 状态 |
|:---|:---|:---|:---|:---|
| **DEV-TICKET-01** | `planner_agent` | 首次双端建档与 60:40 融合权重计算 | 无 | ✅ 已就绪 |
| **DEV-TICKET-02** | `telemetry_agent` | 4维无感物理遥测 (看穿装懂/拦截装累) | T01 | ✅ 已就绪 |
| **DEV-TICKET-03** | `crisis_agent` | 三层隐私屏障与 400-161-9995 心理熔断 | 无 | ✅ 已就绪 |
| **DEV-TICKET-04** | `voice_live_agent` | Qwen-Omni / Gemini Live 全双工实时语音对讲 | T01 | ✅ 已就绪 |
| **DEV-TICKET-05** | `ocr_agent` | 错题 Vision OCR 归因诊断 | 无 | ✅ 已就绪 |
| **DEV-TICKET-06** | `vector_store_agent` | Chroma 0-Token 向量持久化与雷达图 | T01, T04 | ✅ 已就绪 |
| **DEV-TICKET-07** | `parent_portal` | 亲子协同面板与双端推送 | T01, T06 | ✅ 已就绪 |
| **DEV-TICKET-08** | `desktop_tauri_shell` | Tauri 2.0 原生 Windows 桌面软件封装 (.exe) | 全部 | ⭐️ 本次新增 |

---

## 🎫 DEV-TICKET-08 具体执行规范 (桌面端封装)

### 1. 任务目标
使用 Tauri 2.0 将现网 `index.html` 前端与 FastAPI 后端集成，打包编译为一个独立的 Windows 标准桌面安装包：`LearnMate-Agent-OS_v3.0.exe`。

### 2. 执行步骤
1. 安装 Rust 环境：运行 `rustup default stable`
2. 初始化 Tauri 外壳：运行 `npx @tauri-apps/cli init`
3. 配置 `tauri.conf.json`：设置窗口大小 1440x900、标题「智学伴 LearnMate AI Agent OS v3.0」
4. 一键打包编译：运行 `npx tauri build`
5. 交付产物：在 `src-tauri/target/release/bundle/nsis/` 获取 `.exe` 安装包。

### 3. 验收标准
- [ ] 双击 `.exe` 可直接拉起桌面客户端，脱离 Chrome/Edge 浏览器。
- [ ] 8 大 Agent 功能（规划、语音、OCR、遥测、熔断、记忆、亲子端、桌面外壳）100% 顺畅运行。
