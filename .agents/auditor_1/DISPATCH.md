# DISPATCH — Forensic Auditor 1 (Integrity & Anti-Fraud Forensic Auditor)

## Mission
对终稿报告 `d:\AI_Work\人工智能大赛\个性化学习规划_Agent_深度审查与对标评估报告.md` 进行法医级反造假与真实性审计。

## Target Output Path
`d:\AI_Work\人工智能大赛\.agents\auditor_1\audit_report.md`

## Audit Criteria (ZERO TOLERANCE)
1. **No Fake Data / Fabricated References**: 检查引用的 12 篇学术论文/白皮书是否真实存在（如 Corbett & Anderson 1994, Piech 2015, Lord 1980, Sweller 1988, Fogg 2009, Kahneman 2011, Settles & Meeder 2016, Doignon & Falmagne 1999 等），有无虚构作者或无效链接。
2. **No Dummy / Facade Code**: 审查报告中补强建议一中的 Python 代码片段（KalmanFilter, Sigmoid Weight Fuse, Shannon Entropy Monitor），确认其数学逻辑与算法公式真实完整、无假装运行或伪造输出现象。
3. **No Silent Degradation / Instruction Bypassing**: 确认审查过程没有降级、遗漏或跳过任何原始需求 (R1, R2, R3, A1, A2)。
4. **Verdict**: 在 handoff.md 和 audit_report.md 中给出明确的审计结论：CLEAN 或 INTEGRITY VIOLATION。
