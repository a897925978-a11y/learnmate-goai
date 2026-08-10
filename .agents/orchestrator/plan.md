# Plan: 个性化学习规划 Agent 深度审查与对标评估

## Objective
对标 5+ 经典与前沿教育心理学模型以及近 3~5 年主流 AI 自适应学习系统，全面审查【双端建档 + 动态心理学检测】在【个性化学习规划 Agent】中的可行性与盲区，提出 2~3 条极简可落地的高含金量补强建议，最终产出《个性化学习规划 Agent 深度审查与对标评估报告》。

## Milestones & Work Breakdown

### Phase 1: Literature & Saturated Model Benchmark (M1)
- **Assigned Agent**: `teamwork_preview_explorer` (Explorer M1) / `teamwork_preview_spec_miner` (Spec Miner M1)
- **Scope**:
  1. 对标 6 大经典与前沿理论模型：BKT (Bayesian Knowledge Tracing), DKT (Deep Knowledge Tracing), IRT (Item Response Theory), Cognitive Load Theory (Sweller 认知负荷理论), Fogg Behavior Model (B=MAP), Kahneman Dual-System Theory (System 1/2)。
  2. 对标 4 大主流 AI 教育/自适应系统：Knewton (知识图谱与动态调度), Aleks (知识空间理论 KST), Squirrel AI 松鼠 AI (纳米级知识点与 MCM 模式), Duolingo (DASH 记忆衰减与动态复习调度)。
  3. 映射分析：将“首次双端建档 + 60:40 静态/动态融合 + 动态心理检测 + 艾宾浩斯/ZPD 调度”逐项映射对比，梳理学术依据、优势与潜在短板。
- **Output Artifact**: `.agents/explorer_m1/m1_literature_benchmark.md`

### Phase 2: Flaw & Vulnerability Stress Test (M2)
- **Assigned Agent**: `teamwork_preview_critic` (Critic M2) / `teamwork_preview_explorer` (Explorer M2)
- **Scope**:
  1. **60:40 权重鲁棒性/滞后性**: 评估 60% 历史认知 + 40% 动态情绪在突发极峭学情波动（如考前重大挫折、突发焦虑）时的数学分配漏洞、滤波算法缺失导致的时延/过拟合/冷启动异常。
  2. **隐形微问答防疲劳与意图伪装**: 审查每日微摸底在长期使用中的“问答疲劳症”、道德赞许偏见（Social Desirability Bias）、学生对抗性伪装（故意回答“开心”以规避减负，或故意示弱以偷懒）及防篡改机制。
  3. **心理学智库工程可量化性**: 审查阿德勒个体心理学（自卑与超越、目的论）、罗杰斯人本主义（无条件积极关注、自我概念）在 LLM Prompt/规则引擎中的具体量化维度（如 0-1 标量化参数）、心理学伪科学/过度治疗风险防御。
- **Output Artifact**: `.agents/explorer_m2/m2_stress_test.md`

### Phase 3: Laser-focused Actionable Enhancements (M3)
- **Assigned Agent**: `teamwork_preview_worker` (Worker M3)
- **Scope**:
  1. 基于 M1 和 M2 的审查漏洞，提出 2~3 条直接嵌入“个性化学习规划 Agent”的高含金量补强优化建议。
  2. 补强建议需具备：高学术严谨度（符合认知科学/心理学理论）、极简工程落地性（可量化、可代码化）、显著提升 GOAI 竞赛评审认可度。
- **Output Artifact**: `.agents/worker_m3/m3_enhancement_proposals.md`

### Phase 4: Report Synthesis, Review & Audit (M4)
- **Assigned Agents**: `teamwork_preview_worker` (Worker M4 Report Writer), `teamwork_preview_reviewer` (Reviewer M4), `teamwork_preview_auditor` (Auditor M4)
- **Scope**:
  1. 整合 M1、M2、M3 的研究成果，撰写完整、严谨的《个性化学习规划 Agent 深度审查与对标评估报告》。
  2. 报告严格遵守 A1 范围控制（限定在建档+动态心理学检测闭环内）与 A2 对标深度要求。
  3. 部署 Reviewer 审查逻辑严密性与规范性，部署 Auditor 进行反造假与真实性审计。
- **Final Output Artifact**: `d:\AI_Work\人工智能大赛\个性化学习规划_Agent_深度审查与对标评估报告.md`

## Gate Criteria & Quality Standards
- **Range Control**: 100% focused on 【个性化学习规划 Agent】 and its 【建档+动态心理学检测】 loop.
- **Benchmark Depth**: Include at least 5 classic/cutting-edge models with formal mapped equations/concepts and whitepapers.
- **Reviewer Gate**: All reviewers report APPROVE.
- **Auditor Gate**: Auditor reports CLEAN with no integrity/fake data violations.
