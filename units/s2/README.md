# Stage 2 · Agent 核心（W10–W17，101 小时）

**开始前先做**：在 `s2-agent/pyproject.toml` 里声明对 S1 的依赖（`dependencies = ["llm-kit"]` 加 `[tool.uv.sources] llm-kit = { workspace = true }`），然后 `uv sync`。验证 `from llm_kit import LLM` 能 import。详见 [`项目结构.md`](../../docs/项目结构.md)。

**开始前先确认**：`s2-agent/PROJECT.md` 的选题（U1.8）和 `SPEC.md` 的输入输出、异常与验收（U1.9）已经定下来。后面四个阶段全部围绕它。

---

## 单元列表

| 单元 | 时长 | 你会做出什么 |
|---|---|---|
| [U2.1 手写 Agent 循环](U2.1-手写Agent循环.md) | 10h | 200 行以内、不用框架的 Agent，你能逐行讲清楚 |
| [U2.2 工具设计](U2.2-工具设计.md) | 8h | 8 个工具 + 描述写法的对照实验数据 |
| [U2.3 规划与反思](U2.3-规划与反思.md) | 8h | 三种模式的四项指标对比 |
| [U2.4 记忆系统](U2.4-记忆系统.md) | 10h | 跨会话记忆，含冲突和时效处理 |
| [U2.5 RAG 与混合检索](U2.5-RAG与混合检索.md) | 18h | 检索管线、文档治理、权限与删除验证、向量库对照 |
| [U2.6 多 Agent 编排](U2.6-多Agent编排.md) | 10h | 两种模式 + **拆不拆的数据依据** |
| [U2.7 MCP 实战](U2.7-MCP实战.md) | 10h | 一个 server 同时被 Claude Code 和你的 Agent 使用 |
| [U2.9 Skill 与 Plugin](U2.9-Skill与Plugin.md) | 5h | 两个 Skill、可安装的 plugin、触发与效果对照 |
| [U2.10 企业系统集成](U2.10-企业系统集成.md) | 4h | 授权、分页、限流、验签、增量同步与去重演练 |
| [U2.8 框架横评](U2.8-框架横评.md) | 18h | 统一任务对比、术语映射、持久化恢复实验与选型 |

**M2 里程碑**：主线 Agent 的第一个可用版本，**你自己每周真的会用它**。

---

## 开始前必读

Anthropic《[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)》（2024-12-19）。

它定义了五种工作流模式（Prompt Chaining、Routing、Parallelization、Orchestrator-Workers、Evaluator-Optimizer）和一种 Agent 模式。核心建议是：

> **从最简单的方案开始，只在必要时增加复杂度。工作流适合路径确定的任务，Agent 适合需要模型自主决策的开放场景。**

**大多数人做 Agent 的第一个错误，就是本该用工作流的地方用了 Agent。**

其余必读散落在各单元里：U2.2 的工具设计、U2.5 的 Contextual Retrieval、U2.6 的多 Agent 系统、U2.7 的 Code execution with MCP。

---

## 这一阶段的三个重点

**U2.1 不能跳。** 不手写一遍循环，你后面永远只会调框架 API，遇到问题不知道从哪查。200 行以内，每一行你都要能讲清楚。

**每个单元都有对照实验。** U2.2 比工具描述、U2.3 比三种模式、U2.5 比四档检索配置、U2.6 比拆不拆、U2.8 比三个框架。**这不是为了写报告，是为了训练「用数据做决策」的习惯**——S3 整个阶段就是把这件事自动化。

**「不做」也是结论。** 如果你测出来单 Agent 比多 Agent 好、手写循环比框架够用，**把数据和理由写清楚，这一样是完成，而且更有说服力。**

---

## 复杂度阶梯

做任何架构决策前，回到这个阶梯，问自己「我真的需要上一级吗」：

```
单次调用
  < 工作流（写死的步骤）
    < ReAct 循环
      < Plan-and-Execute
        < 加 Reflexion
          < 多 Agent
```

**每上一级都要有数据支持。** 「我觉得这样更高级」不是理由。
