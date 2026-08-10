# [开发工单集] 个性化学习规划 Agent — 7 大模块工程开发任务单

> **手册用途**：提供开箱即用、零沟通成本的**标准化工程开发任务单 (Developer Spec Tickets)**。涵盖 7 大任务包的输入输出契约、核心伪代码/逻辑步骤、边界异常处理与单元测试断言。

---

## 📋 任务单 1：双端初始建档与 Vision OCR 摸底模块 (DEV-TICKET-01)

*   **工单编号**：`DEV-TICKET-01`
*   **模块名称**：双端初始建档与 Vision OCR 试卷摸底引擎
*   **目标**：采集家长端学籍/期望及学生端首张卷子 Vision OCR，生成初始学情 JSON 档案。

### 1. 输入契约 (Input Schema)
```json
{
  "parent_profile": {
    "parent_id": "P_1001",
    "grade": "junior_2",
    "textbook": "人教版",
    "subject": "数学",
    "exam_node": "monthly_exam",
    "target_score": 90,
    "parent_tags": ["粗心", "缺乏自信"]
  },
  "student_profile": {
    "student_id": "S_2001",
    "image_base64_or_url": "https://cdn.edu.com/exam_paper_01.jpg",
    "learning_style": "visual",
    "interests": ["Minecraft", "原神"]
  }
}
```

### 2. 核心处理步骤与伪代码
1. 校验输入图片路径与 Pydantic 字段非空。
2. 调用 Gemini 2.5 Vision API，系统提示词要求输出结构化错题与归因：
   - 提取错题得分与总分；
   - 将错因归类为 `[CARELESS_ERROR, CONCEPT_BLURRY, NO_IDEA]` 三类之一。
3. 建立 `GrowthProfile` 数据结构，将扣分最高前 3 个知识点标记为 `initial_weaknesses`。

### 3. 输出契约 (Output Schema)
```json
{
  "profile_id": "PROFILE_S2001_P1001",
  "initial_score": 58.5,
  "deduction_map": {"二次函数": 12, "勾股定理": 8},
  "error_attributions": {"二次函数": "CONCEPT_BLURRY", "勾股定理": "CARELESS_ERROR"},
  "initial_weaknesses": ["二次函数图像性质", "勾股定理应用"],
  "student_interests": ["Minecraft", "原神"]
}
```

### 4. 单元测试与验收标准
- [ ] 测试用例 `test_ocr_parser_valid_image`：必须成功解析并返回 `deduction_map` 字典。
- [ ] 测试用例 `test_missing_parent_tag`：缺失标签时须自动补默认空列表 `[]`。

---

## 📋 任务单 2：卡尔曼去噪与 Sigmoid 断崖熔断引擎 (DEV-TICKET-02)

*   **工单编号**：`DEV-TICKET-02`
*   **模块名称**：卡尔曼-EWMA 心理去噪与 Sigmoid 非线性相变熔断算控
*   **目标**：算控 `W_composite` 综合得分，当心理崩溃时触发 Sigmoid 断崖熔断防护。

### 1. 输入契约 (Input Schema)
```json
{
  "s_static_history": 0.85,
  "s_dynamic_raw": 0.10,
  "sample_count_N": 45,
  "parent_target_score": 95
}
```

### 2. 核心处理伪代码
```python
# 1. 1D 卡尔曼滤波更新
P_prime = P + Q
K_gain = P_prime / (P_prime + R_noise)
s_dynamic_filtered = x_hat + K_gain * (s_dynamic_raw - x_hat)

# 2. Sigmoid 相变熔断
if s_dynamic_filtered < 0.25:  # 断崖阈值
    w_dynamic = 0.85  # 强制接管
else:
    w_dynamic = 0.40 + 0.45 / (1.0 + math.exp(-(0.25 - s_dynamic_filtered) / 0.05))

# 3. 置信度计算与归一化
confidence = 1.0 - math.exp(-sample_count_N / 30.0)
w_static_effective = (1.0 - w_dynamic) * confidence
w_sum = w_dynamic + w_static_effective

w_dynamic_final = w_dynamic / w_sum
w_static_final = w_static_effective / w_sum

w_composite = w_static_final * s_static_history + w_dynamic_final * s_dynamic_filtered
```

### 3. 输出契约 (Output Schema)
```json
{
  "w_composite": 0.2125,
  "w_dynamic": 0.85,
  "w_static": 0.15,
  "is_fused": true,
  "mediator_popup": {
    "triggered": true,
    "suggestion": "检测到学生突发情绪重挫，已自动下调本日难度50%，并为您开启亲子破冰卡。"
  }
}
```

### 4. 单元测试与验收标准
- [ ] 断言：当 `s_dynamic_raw = 0.10` 时，`is_fused` 必须为 `True` 且 `w_dynamic >= 0.80`。
- [ ] 断言：`w_composite` 必须在相变后降低至 $0.30$ 以下，阻断难题推送。

---

## 📋 任务单 3：无感物理遥测与抗作弊检测模块 (DEV-TICKET-03)

*   **工单编号**：`DEV-TICKET-03`
*   **模块名称**：无感行为物理遥测与博弈残差判定引擎
*   **目标**：收集打字时延、删改率、悬停时间，拦截装懂与假装疲惫刷低难度的作弊行为。

### 1. 输入契约 (Input Schema)
```json
{
  "explicit_self_rating": 0.95,
  "telemetry_metrics": {
    "first_token_latency_ms": 4200,
    "edit_distance_ratio": 0.45,
    "hover_pause_count": 5,
    "response_time_sec": 0.7
  },
  "historical_shannon_entropy": 0.15
}
```

### 2. 核心处理伪代码
```python
# 1. 回归模型估计真实状态
s_predicted = 1.0 - (0.4 * edit_ratio + 0.3 * (latency_ms / 5000) + 0.3 * (hover_count / 10))

# 2. 博弈残差判定
delta_gaming = explicit_self_rating - s_predicted

if delta_gaming > 0.25:
    gaming_type = "POSITIVE_GAMING"  # 装懂
    effective_rating = s_predicted   # 强制使用遥测预测值
elif delta_gaming < -0.25:
    gaming_type = "NEGATIVE_GAMING"  # 假装疲惫
    effective_rating = explicit_self_rating
    lock_zpd_downgrade = True         # 锁定减负降级，注入探针题

# 3. 香农熵防脱敏判定
if response_time_sec < 0.8 and historical_shannon_entropy < 0.20:
    silent_telemetry_switch = True   # 静默停用问答 7 天
```

### 3. 输出契约 (Output Schema)
```json
{
  "gaming_type": "POSITIVE_GAMING",
  "effective_rating": 0.38,
  "silent_telemetry_switch": true,
  "action_taken": "屏蔽显式自评，强制下调自适应权重，注入探针诊断题。"
}
```

### 4. 单元测试与验收标准
- [ ] 断言：`explicit = 0.95, latency = 4200ms` 必须返回 `POSITIVE_GAMING`。
- [ ] 断言：`entropy < 0.20` 必须返回 `silent_telemetry_switch = True`。

---

## 📋 任务单 4：(A, R) 心理状态机与 Tier 3 临床硬熔断 (DEV-TICKET-04)

*   **工单编号**：`DEV-TICKET-04`
*   **模块名称**：(A, R) 双轴心理 FSM 与 Tier 3 临床安全熔断屏障
*   **目标**：消除 LLM 随机鸡汤文本，遇到高危心理语义瞬间硬性切断拟人对话。

### 1. 输入契约 (Input Schema)
```json
{
  "user_text_input": "我觉得活着没什么意思，想自残划伤自己",
  "adler_A_score": -0.6,
  "rogers_R_score": 0.2
}
```

### 2. 核心处理逻辑
1. **高危语义正则与 Embedding 扫描**：匹配自残、自杀、绝望关键词词库。
2. 若匹配度 $\ge 0.90$：
   - 触发 `Tier 3` 硬熔断；
   - 阻断 Prompt 生成，禁止任何 AI 心理治疗对话；
   - 渲染热线 UI （**400-161-9995**）。
3. 若无高危风险：
   - 根据 $(A, R)$ 标量落入 4 象限确定当前状态（如 $S1$ 脆弱保护区）；
   - 输出控制标量 JSON（`empathy_level=0.90`, `task_autonomy_ratio=1.0`）注入 System Prompt。

### 3. 输出契约 (Output Schema)
```json
{
  "trigger_tier": 3,
  "is_ai_blocked": true,
  "ui_action": "RENDER_HOTLINE_400_161_9995",
  "system_prompt_contract": null,
  "alert_encrypted_payload": "CRISIS_EVENT_LOG_ENCRYPTED"
}
```

### 4. 单元测试与验收标准
- [ ] 断言：包含“自残”语义时，`is_ai_blocked` 必须等于 `True`。
- [ ] 断言：严禁向控制台暴露未经加密的危机敏感词字符串。

---

## 📋 任务单 5：动态 ZPD 心流调度与睡眠保护引擎 (DEV-TICKET-05)

*   **工单编号**：`DEV-TICKET-05`
*   **模块名称**：最近发展区 (ZPD) 心流调度与 22:00 深夜睡眠保护锁
*   **目标**：保持“一鼓作气”学习心流，连错 2 题推 30s AI 视频，晚 22:00 强制锁定劝睡。

### 1. 输入结构
```json
{
  "streak_correct": 0,
  "streak_incorrect": 2,
  "current_time_str": "22:15",
  "is_weekday": true
}
```

### 2. 核心处理伪代码
```python
# 1. 深夜睡眠保护判断
if current_time_str >= "22:00":
    return {
        "status": "SLEEP_LOCKOUT",
        "message": "太晚了，今天辛苦了，赶紧睡觉吧！",
        "lock_active": True
    }

# 2. 心流微调度
if streak_correct >= 3:
    action = "LEVEL_ACCELERATION"  # 跳过低效题，冲高阶题
elif streak_incorrect == 2:
    action = "BUFFER_DOWNGRADE"    # 触发降级缓冲，自动调取 30s AI 视频
elif streak_incorrect >= 4:
    action = "STOP_LOSS_ARCHIVE"   # 止损入艾宾浩斯库，结束本节练习
```

### 3. 输出契约 (Output Schema)
```json
{
  "status": "BUFFER_DOWNGRADE",
  "video_trigger": {
    "fetch_video_id": "VID_MATH_QUADRATIC_30S",
    "video_title": "30秒动画搞懂二次函数对称轴"
  },
  "next_difficulty": 0.40
}
```

### 4. 单元测试与验收标准
- [ ] 断言：当 `current_time_str = "22:05"` 时，必须返回 `SLEEP_LOCKOUT` 且锁定练习。
- [ ] 断言：当 `streak_incorrect = 2` 时，必须返回 `fetch_video_id`。

---

## 📋 任务单 6：Chroma 向量库落库与多阶报告引擎 (DEV-TICKET-06)

*   **工单编号**：`DEV-TICKET-06`
*   **模块名称**：每次学习短日报落库与周/月/年多阶成长轨迹报告
*   **目标**：做题结束即刻向量化落库 ChromaDB，生成可视化成长轨迹。

### 1. 输入结构
```json
{
  "student_id": "S_2001",
  "session_id": "SESS_8891",
  "topics_covered": ["二次函数"],
  "score_delta": +15,
  "emotion_summary": "良好"
}
```

### 2. 核心处理步骤
1. 格式化 JSON 成为文本 Embeddings 字符串。
2. 调用 ChromaDB 本地 Client，存入 `collection("student_daily_digests")`。
3. 统计过去 7 天 / 30 天向量数据，计算掌握度雷达图百分比。

### 3. 输出契约 (Output Schema)
```json
{
  "daily_digest_id": "DIGEST_8891",
  "chroma_doc_id": "DOC_S2001_20260809",
  "radar_scores": {"记忆": 85, "理解": 70, "应用": 60, "分析": 45},
  "weekly_trend_url": "/api/reports/weekly_S2001.pdf"
}
```

---

## 📋 任务单 7：双端 UI/UX 视图与演示宣介包 (DEV-TICKET-07)

*   **工单编号**：`DEV-TICKET-07`
*   **模块名称**：学生端关卡地图 + 家长端倒计时 + 3分钟 Demo 视频与路演 PPT
*   **目标**：开发前端双端交互界面，导出 3 分钟宣介视频与路演 PDF。

### 1. 核心开发步骤
1. **学生端**：写 Vue/React 组件，渲染游戏化关卡地图、做题悬浮窗、30s 短视频播放弹窗。
2. **家长端**：渲染冲刺进度条、亲子破冰建议卡片、22:00 睡眠倒计时。
3. 录制 3 分钟 Demo 演示视频（MP4）并制作 15 页路演 PPT。

### 2. 交付文件路径
- 前端源码：`frontend/src/views/`
- 演示视频：`d:\AI_Work\人工智能大赛\demo_3min.mp4`
- 路演 PPT：`d:\AI_Work\人工智能大赛\roadshow_pitch.pdf`
