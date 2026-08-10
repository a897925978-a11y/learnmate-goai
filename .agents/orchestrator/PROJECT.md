# Project: 个性化学习规划 Agent 深度审查与对标评估

## Architecture
- Module 1: 首次双端建档 (家长端视角 + 学生端自评 + 基础认知能力基线)
- Module 2: 60:40 静态/动态权值融合引擎 (60% 历史认知状态 + 40% 动态心理学/生理/情绪检测)
- Module 3: 隐形微摸底/微问答防疲劳与意图伪装防御机制
- Module 4: 心理学大师智库 (阿德勒/罗杰斯/皮亚杰) 可量化工程落地与 ZPD (近侧发展区) 动态微调度
- Module 5: 三层隐私屏障与数据合规闭环

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | 教育模型饱和对标 | BKT, DKT, IRT, Cognitive Load Theory, Fogg Model, Kahneman Dual-System 等与 60:40+ZPD 映射对比 | M1 | R1 |
| 2 | 主流 AI 教育系统白皮书与文献对比 | Knewton, Aleks, Squirrel AI 松鼠AI, Duolingo 等近3~5年白皮书及学术文献对标 | M1 | R1 |
| 3 | 60:40 权重波动的鲁棒性/滞后性审查 | 极陡峭学情波动（考前挫折/突发情绪）下静态/动态权重分配的数学与工程破绽及改善机制 | M2 | R2 |
| 4 | 隐形微问答防疲劳与伪装防御审查 | 长周期微问答疲劳、道德赞许性偏见 (Social Desirability Bias)、意图伪装识别与应对方案 | M2 | R2 |
| 5 | 心理学大师智库工程化可量化性审查 | 阿德勒个体心理学、罗杰斯人本主义具体量化参数、规则引擎落地性及防心理学伪科学风险 | M2 | R2 |
| 6 | 高含金量补强优化建议 | 提出 2~3 条高创新度、极简可落地的嵌入式补强建议（拉升学术与工程严谨性） | M3 | R3 |
| 7 | 深度审查与对标评估报告终稿 | 撰写完整的《个性化学习规划 Agent 深度审查与对标评估报告》并交付 | M4 | Synthesis |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: 理论与系统饱和对标 | R1: 5+ 经典/前沿教育模型及 4 大主流 AI 自适应系统映射对比 | none | DONE |
| 2 | M2: 盲区与破绽压力测试 | R2: 60:40 权重滞后性、微问答防疲劳与意图伪装、心理学智库量化落地深度审查 | M1 | DONE |
| 3 | M3: 补强优化方案设计 | R3: 2~3 条高含金量嵌入式补强建议（学术+工程） | M1, M2 | DONE |
| 4 | M4: 报告合成与审定 | 最终报告《个性化学习规划 Agent 深度审查与对标评估报告》合成、审查与审计 | M1, M2, M3 | DONE |

## Interface Contracts
### Research Outputs ↔ Report Structure
- M1 Output: `.agents/explorer_m1/m1_literature_benchmark.md`
- M2 Output: `.agents/explorer_m2/m2_stress_test.md`
- M3 Output: `.agents/worker_m3/m3_enhancement_proposals.md`
- M4 Final Report: `d:\AI_Work\人工智能大赛\个性化学习规划_Agent_深度审查与对标评估报告.md`

## Code Layout
- `.agents/orchestrator/` — Orchestrator metadata, briefing, plan, progress, project files
- `.agents/explorer_m1/` — M1 research files
- `.agents/explorer_m2/` — M2 stress test research files
- `.agents/worker_m3/` — M3 enhancement proposals draft
- `.agents/worker_m4/` — M4 report drafting
- `.agents/reviewer_m4/` — Reviewer evaluation report
- `.agents/auditor_m4/` — Forensic audit evaluation
