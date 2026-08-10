# 🖥️ [桌面端架构文档] Tauri 2.0 原生实时语音 Agent 软件开发方案

> **定位**：放弃网页端限制，将项目全面升级为 **标准的 Windows 桌面客户端 (.exe 软件)**。  
> 采用 **Tauri 2.0 (Rust 硬件极速外壳 + 现网高颜值前端)** 架构，彻底解决浏览器切屏休眠、Autoplay 自动播放锁与全屏局限问题。

---

## 一、 桌面客户端整体拓扑与优势

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│              「智学伴 LearnMate」Tauri 2.0 原生桌面客户端架构                  │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  [Windows 桌面客户端 (Tauri 2.0 .exe 软件外壳)]                                 │
│  ├─ 1. 原生窗口 / 桌面右下角透明悬浮小狐狸 (Global Mascot Overlay)             │
│  ├─ 2. Rust 底层 (`src-tauri`) ──> 全局快捷键 (`Alt + V`) / 硬件 PCM 声卡直连  │
│  ├─ 3. Webview 视图引擎 ───────> 100% 复用现有 `index.html` 高颜值 UI          │
│  └─ WebSocket Client ──────────> 直连本地 Backend (`ws://127.0.0.1:8000/...`)   │
│                                │ ▲                                              │
│                                ▼ │ (全双工双向 TCP / WebSocket 通道)            │
│  [Python FastAPI 后端伴学中枢 (Engine Server)]                                  │
│  └─ Qwen-Omni Realtime WSS Proxy / Vector Store 记忆持久化                     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 桌面端 4 大绝对优势：
1. **彻底防休眠 (Zero Tab Throttling)**：后台切屏看论文、写 Word 时，语音通信 24 小时保持 300ms 敏捷对讲。
2. **彻底无自动播放锁 (No Autoplay Security Lock)**：原生软件环境，双击启动即接通音频，无需用户手动点击解锁。
3. **全局悬浮与快捷键 (Global Hotkeys)**：支持按下 `Alt + V` 随时语音打断或唤醒。
4. **轻量与极致性能**：安装包 $<15\text{MB}$，内存占用 $<45\text{MB}$。

---

## 二、 桌面项目目录结构

在 `d:\AI_Work\人工智能大赛\` 根目录下构建 Tauri 2.0 项目包：

```
d:\AI_Work\人工智能大赛\
├── backend/                         # 原有 Python FastAPI 后端
├── src-tauri/                       # Tauri 2.0 Rust 原生外壳目录
│   ├── Cargo.toml                   # Rust 依赖 (tauri v2, tauri-plugin-global-shortcut)
│   ├── tauri.conf.json              # 桌面软件配置文件 (窗口大小、图标、透明度)
│   └── src/
│       └── main.rs                  # Rust 主入口 (初始化全局热键与本地桥接)
├── index.html                       # 100% 复用现有 UI 前端
└── Cargo.lock
```

---

## 三、 `tauri.conf.json` 标准配置规范

```json
{
  "$schema": "https://schema.tauri.app/config/2",
  "productName": "LearnMate-Agent-OS",
  "version": "3.0.0",
  "identifier": "com.learnmate.agent.os",
  "build": {
    "frontendDist": "../index.html",
    "devUrl": "http://127.0.0.1:8000"
  },
  "app": {
    "windows": [
      {
        "title": "「智学伴 LearnMate AI Agent OS v3.0」桌面版",
        "width": 1440,
        "height": 900,
        "resizable": true,
        "fullscreen": false,
        "decorations": true,
        "transparent": false,
        "center": true
      }
    ],
    "security": {
      "csp": null
    }
  },
  "bundle": {
    "active": true,
    "targets": ["msi", "nsis"],
    "icon": [
      "icons/icon.png"
    ]
  }
}
```

---

## 四、 编译打包与交付流程

1. **依赖环境准备**：
   - Rust 环境 (`rustup default stable`)
   - Node.js (`npx`)
2. **打包命令**：
   ```bash
   npx tauri build
   ```
3. **产物输出**：
   - 安装包位置：`src-tauri/target/release/bundle/nsis/LearnMate-Agent-OS_3.0.0_x64-setup.exe`
