# DISPATCH — Explorer M1 (Literature & Saturated Model Benchmark)

## Mission
深入调查与饱和对标经典及前沿教育模型（BKT, DKT, IRT, Cognitive Load Theory, Fogg Model, Kahneman Dual-System Theory等），以及近 3~5 年主流 AI 教育/自适应学习系统（Knewton, Aleks, Squirrel AI 松鼠AI, Duolingo 等）白皮书与学术文献。

## Target Output Path
`d:\AI_Work\人工智能大赛\.agents\explorer_m1\m1_literature_benchmark.md`

## Detailed Instructions
1. **5+ 经典/前沿教育心理模型饱和对标**:
   - Bayesian Knowledge Tracing (BKT): 隐马尔可夫模型参数（P(L0), P(T), P(S), P(G)），在连续知识追踪中的优势与缺乏上下文/情绪状态维度的缺陷。
   - Deep Knowledge Tracing (DKT / Dynamic Key-Value Memory Networks): 基于 RNN/LSTM/Transformer 的端到端知识追踪，高维表征能力 vs. 可解释性黑盒问题。
   - Item Response Theory (IRT / 3PL-IRT): 试题难度 (b)、区分度 (a)、猜测度 (c) 标定能力，与“首次双端建档”中冷启动基线测量的关系。
   - Cognitive Load Theory (Sweller 认知负荷理论): 内在负荷 (Intrinsic)、外在负荷 (Extraneous)、胜任负荷 (Germane)，以及认知超载时的防疲劳微调策略。
   - Fogg Behavior Model (B=MAP): 动机 (Motivation)、能力 (Ability)、提示 (Prompt)，在每日微摸底/微问答触发时机与动态规划调控中的应用。
   - Kahneman Dual-System Theory (System 1/2): 系统1 (直觉/情绪) 与 系统2 (理性/认知) 交互，支撑 60% 系统2认知历史 + 40% 系统1实时情绪/心理状态动态融合的学术合理性。

2. **4 大主流 AI 教育/自适应学习系统深度剖析**:
   - Knewton: 知识图谱 (Knowledge Graph) 依赖、自适应推荐引擎、动态路径调度白皮书与工程架构对比。
   - ALEKS: 知识空间理论 (Knowledge Space Theory, KST) 与非连通知识态迁移，与双端建档中前置知识图谱基线映射。
   - Squirrel AI (松鼠AI): 纳米级知识点拆解 (Nanoscale Knowledge Components) 与 MCM (Model of Content, Capacity, Methodology) 模式对比。
   - Duolingo: DASH (Difficulty-Adjustment Half-Life) 记忆衰减算法、动态复习调度、游戏化微互动与微问答对比。

3. **逐项映射对比矩阵**:
   - 建立详细的映射对比表格，将我方“首次双端建档 + 60:40 静态/动态加权 + 动态心理检测 + 艾宾浩斯/ZPD 调度”与上述模型/系统进行维度对标（理论根基、冷启动能力、动态调控灵敏度、心理/生理维度融合、可解释性）。

4. **学术与工程规范**:
   - 包含真实的学术文献引用（作者、年份、经典论文/白皮书名称）。
   - 严格限定在【个性化学习规划 Agent】及其【建档+动态心理学检测】闭环内，不得越界到后续教案生成或渲染模块。

5. **交付要求**:
   - 在 `.agents/explorer_m1/` 中撰写 `progress.md` 和 `handoff.md`。
   - 将完整对标研究成果写入 `d:\AI_Work\人工智能大赛\.agents\explorer_m1\m1_literature_benchmark.md`。
