# 🎫 [DEV-TICKET-08] Tauri 2.0 桌面端软件打包与原生硬件集成工单

| 工单属性 | 详细内容 |
|:---|:---|
| **工单编号** | `DEV-TICKET-08` |
| **模块名称** | `desktop_tauri_shell` (桌面端标准软件封装) |
| **负责人** | 开发者 (荆广伟 / 代码 Agent) |
| **前置依赖** | `DEV-TICKET-01` ~ `DEV-TICKET-07`，Rust 开发环境 |
| **难度等级** | ⭐️⭐️⭐️ (标准搭建外壳，难度适中) |

---

## 一、 任务目标

将「智学伴 LearnMate」全面封装打包为 **Windows 标准桌面软件 (.exe 安装包)**：
1. 使用 Tauri 2.0 给现有的 `index.html` 前端搭一个极轻量的 Rust 原生软件外壳。
2. 彻底摆脱 Chrome/Edge 浏览器切屏休眠、挂起与自动播放限制。
3. 编译打出一个标准可双击运行的 `LearnMate-Agent-OS_setup.exe` 桌面软件。

---

## 二、 4 步傻瓜式操作流程

### 步骤 1：初始化 Tauri 2.0 原生外壳
在根目录 `d:\AI_Work\人工智能大赛\` 打开终端，运行：
```bash
npx @tauri-apps/cli init
```
*   App name: `LearnMate-Agent-OS`
*   Window title: `「智学伴 LearnMate AI Agent OS v3.0」`
*   Web assets path: `../index.html`
*   URL: `http://127.0.0.1:8000`

### 步骤 2：配置 `tauri.conf.json`
将项目中的 [桌面端_Tauri2_实时语音Agent_架构设计与开发文档.md](file:///d:/AI_Work/%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E5%A4%A7%E8%B5%9B/%E6%A1%8C%E9%9D%A2%E7%AB%AF_Tauri2_%E5%AE%9E%E6%97%B6%E8%AF%AD%E9%9F%B3Agent_%E6%9E%B6%E6%9E%84%E8%AE%BE%E8%AE%A1%E4%B8%8E%E5%BC%80%E5%8F%91%E6%8F%90%E7%A4%BA%E8%AF%8D.md) 中的 JSON 配置覆盖复制到 `src-tauri/tauri.conf.json`。

### 步骤 3：桌面客户端联调测试
运行调试指令，拉起本地桌面窗口：
```bash
npx tauri dev
```

### 步骤 4：一键编译打包 `.exe`
确认调试无误后，运行终极打包指令：
```bash
npx tauri build
```
编译完成后，可在 `src-tauri/target/release/bundle/nsis/` 目录下拿到标准的 `.exe` 软件安装包！

---

## 三、 验收标准与测试断言

- [ ] **软件形态**：成功双击 `.exe` 拉起独立的桌面客户端窗口，不依赖 Chrome/Edge 浏览器。
- [ ] **后台切屏对讲**：最小化桌面软件或切到其他软件看文档时，实时语音通信**流畅对讲不中断**。
- [ ] **安装包体积**：生成的 `.exe` 安装包大小 $< 20\text{MB}$。
