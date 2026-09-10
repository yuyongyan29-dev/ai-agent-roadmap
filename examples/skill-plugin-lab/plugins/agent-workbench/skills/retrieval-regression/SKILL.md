---
name: retrieval-regression
description: 比较主线 Agent 两次检索的命中结果。用户要求检查检索改动是否回退、对比 baseline 和 candidate 的 case 结果时使用；不用于评判回答文风、接口部署或没有基线的数据。
---

# 检索回归检查

1. 确认用户提供 baseline、candidate 两个 JSON 路径，每个元素含唯一 `case_id` 和布尔型 `hit`。
2. 执行本技能目录下 `scripts/compare.py BASELINE CANDIDATE`。先定位本 `SKILL.md` 的绝对路径，再从其所在目录找脚本；不要假设插件位于用户当前工作目录。
3. 退出码 0 表示没有 `true → false` 的 case；退出码 1 表示出现回归；退出码 2 表示输入不合法或 case 集不一致。
4. 如实报告退出码、命中数量、回归 case。不要把这个布尔命中检查叫完整 RAG 质量评估，也不要改数据使检查通过。
5. 回归时只建议先检查哪个 case，是否修改实现由用户任务决定。
