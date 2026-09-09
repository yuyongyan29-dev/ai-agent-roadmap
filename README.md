# AI Agent 系统学习计划（零代码基础 → 生产级）

> 版本：2026-09-09 · 周期 27 周 · 每周 20 小时 · 总投入约 532 小时
> 飞书文档：https://dcnxpg5pruao.feishu.cn/docx/HEKGdkG7EofGpgx3NwScJt70nbf
> 目标：独立做 Agent 应用 + 看懂并参与 Agent 平台基建 + 能在业务里落地 + 能拿去面试 + 顺带能做网站/App/小程序

**第一次打开？先读 [`从这里开始.md`](从这里开始.md)**（[飞书版](https://dcnxpg5pruao.feishu.cn/docx/JgSPd46vBobhH7xBLZkcYQvZnwb)）—— VS Code 配置、每个单元的固定五步、前三天的具体清单。

**七个阶段的项目怎么互相引用？** 见 [`项目结构.md`](项目结构.md)（[飞书版](https://dcnxpg5pruao.feishu.cn/docx/RyY1dimYxonwLWxiFAMccaRPnwe)）—— uv workspace、跨阶段依赖、csvstats 怎么承接。

**每个单元的详细拆解在 [`units/`](units/) 目录**，本文件是总览和索引。

| 阶段 | 本地文档 | 飞书 |
|---|---|---|
| **S0 工程地基** | [units/s0/](units/s0/README.md) · 10 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/Cz1tdfwWQoE2e3xdAwTcd4gMntc) |
| **S1 LLM 基础与上下文工程** | [units/s1/](units/s1/README.md) · 8 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/XNhHdGuluooLYIxW77icPDObnPH) |
| **S2 Agent 核心** | [units/s2/](units/s2/README.md) · 8 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/LhQEdf8bao3QscxBV5bcf3YEnKg) |
| **S3 评估与可观测性** | [units/s3/](units/s3/README.md) · 8 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/KtPTdlMMLoryUCx92rLc8IYxnjd) |
| **S4 生产化** | [units/s4/](units/s4/README.md) · 8 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/EryudVmikoTYXfxfqL8cpl8RnCd) |
| **S5 产品外壳** | [units/s5/](units/s5/README.md) · 7 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/HwAvdsE1NoxdV1xp2d3cQ4MWnVe) |
| **S6 平台基建与面试** | [units/s6/](units/s6/README.md) · 6 个单元 | [打开](https://dcnxpg5pruao.feishu.cn/docx/A5kFdhiJKoqrxyxxuHLcp2Cenof) |

---

## 0. 这份计划怎么用

三条规则，比计划本身更重要。

**每个单元都必须留下一个能跑的东西。** 不是笔记，是代码、是能打开的页面、是能贴出来的截图。看完视频没有产出，这个单元就不算完成。

**按单元推进，不按章节推进。** 每个单元标了预计耗时和「完成判据」。判据没达到就不勾选，宁可拖一周也不要虚勾。

**每周留 4 小时写复盘。** 在 `logs/` 目录下按 `2026-W37.md` 命名，写三件事：这周做出了什么、卡在哪、下周第一件事做什么。这份日志后面直接变成你的面试素材。

目录结构：

```
ai-agent-roadmap/
├── README.md          # 本文件
├── 项目结构.md        # 七个阶段怎么串起来（S1 开始前必读）
├── 从这里开始.md      # 上手指南，第一次打开先读这个
├── templates/         # 单元笔记与周复盘模板
├── .vscode/           # VS Code 插件与设置
├── units/
│   ├── s0/            # 9 个单元，教程级细度
│   ├── s1/            # 8 个单元，教程级细度
│   └── s0/ … s6/      # 54 个单元，每个一个文件
├── logs/              # 每周复盘
├── s0-foundation/     # 各阶段代码
├── s1-llm/
├── s2-agent/
├── s3-eval/
├── s4-production/
├── s5-frontend/
└── s6-platform/
```

---

## 1. 总览

| 阶段 | 主题 | 周次 | 时长 | 里程碑产出 |
|---|---|---|---|---|
| S0 | 工程地基 | W1–W4 | 72h | M0 带测试和 Docker 的 REST API |
| S1 | LLM 基础与上下文工程 | W5–W7 | 60h | M1 命令行 LLM 工具 |
| S2 | Agent 核心 | W8–W11 | 80h | M2 你自己场景的可用 Agent |
| S3 | 评估与可观测性 | W12–W15 | 80h | M3 给 M2 建完整 eval 与 trace |
| S4 | 生产化 | W16–W19 | 80h | M4 M2 真正上线，带灰度和 SLO |
| S5 | 产品外壳 | W20–W23 | 80h | M5 Web 前端 + 小程序入口 |
| S6 | 平台与基建 | W24–W27 | 80h | M6 mini agent runtime + 作品集 |

一条主线贯穿全程：**S2 做出来的那个 Agent，S3 给它建评估，S4 让它上线，S5 给它做界面，S6 把它的运行时拆开重写一遍。** 六个里程碑不是六个玩具，是同一个东西的六次升级。

选题在 S1 结束时定下来，标准是：你自己每周真的会用、有明确的对错、涉及至少三个外部工具。详见 S1 的 U1.8。

---

## 2. 每周节奏

| 项 | 时长 | 说明 |
|---|---|---|
| 输入 | 5h | 看文档、读源码、看课程。输入永远是最小的一块 |
| 动手 | 11h | 写代码、调试、跑实验 |
| 复盘与整理 | 4h | 周复盘、整理笔记、补测试、写 README |

工作日每天 2 小时，周末各 5 小时，是最容易坚持的分布。

**遇到卡点先自己撞 30 分钟，撞不动立刻问 AI，但要求它解释而不是给答案。** 零基础阶段最大的风险不是学得慢，是全程让 AI 代写、最后什么都不会。给自己定个规矩：S0 和 S1 阶段的代码，每一行你都要能口头解释。

---

## 3. 技术栈决策

一次定好，中途不换。选型理由都写在这里，以后有人问你「为什么用这个」你直接答得出来。

**主语言 Python。** Agent 生态的默认语言。包管理用 `uv`，2026 年新项目的默认选择。

**第二语言 TypeScript。** 前端和小程序必须用。S5 之前不用碰。

**后端 FastAPI。** 异步原生、自动生成 OpenAPI 文档、和 Pydantic 打通。

**Agent 框架：先手写，再横评，再选一个。**
S2 前两周不用任何框架，自己写 ReAct 循环——不这样做，你会永远不知道框架在替你做什么。之后花一个单元横评 LangGraph、OpenAI Agents SDK、Claude Agent SDK、smolagents，用数据选一个。**不要在选框架上花超过一个单元的时间。**

**协议：MCP 必学，A2A 了解。** MCP 解决 Agent 怎么用工具，已被 Claude、ChatGPT、VS Code、Cursor 等广泛支持；A2A 解决 Agent 之间怎么委派任务，已发布 v1.0，由 Linux 基金会下的技术指导委员会维护，成员含 AWS、Cisco、Google、IBM Research、Microsoft、Salesforce、SAP、ServiceNow。企业架构里两者通常一起用。

**检索：Postgres + pgvector 起步。** 不要一上来就上专用向量库。检索策略用 hybrid：向量 + BM25，RRF 融合，再 rerank。**每一步的收益必须在你自己的语料上实测，不要信任何博客上的数字。**

**可观测性：Langfuse 自托管。** 开源、可自部署，trace、评估、成本分析在一处。埋点遵循 OpenTelemetry 的 GenAI 语义约定，这样以后换平台不用重写。

**前端：Next.js + TypeScript + Tailwind + Vercel AI SDK。**

**小程序：Taro。** 用 React 语法，S5 学的 React 直接复用。

**模型：至少同时接三家。** 海外 Claude / GPT，国内 DeepSeek / 通义 / Kimi / 豆包。用 LiteLLM 做统一抽象层，这是后面做成本路由的前提。

### 版本基线（2026-09-09 从 npm 与 PyPI 官方源核实）

| 包 | 版本 | 包 | 版本 |
|---|---|---|---|
| next | 16.3.4 | langgraph | 1.2.11 |
| react | 19.2.8 | openai-agents | 0.22.2 |
| typescript | 7.0.2 | claude-agent-sdk | 0.2.152 |
| tailwindcss | 4.3.3 | fastapi | 0.141.1 |
| ai (Vercel AI SDK) | 7.0.95 | mcp | 2.2.0 |
| @openai/agents | 0.17.2 | uv | 0.12.12 |

**动手前再核一次。** 这个领域三个月就能变一轮，尤其是前端。

---

## 4. 大厂真实业务流里的「基本操作」

下面每一条都是 2026 年在真实生产环境里默认要做的事。学完整个计划，你应该对每一条都亲手实践过。

**评估驱动，不靠体感。** 改一版 prompt 就跑一次离线评估集，分数掉了就不发。没有评估集的 Agent 项目进不了发布流程。

**全链路 trace。** 每一轮对话、每次工具调用、每次模型推理都要有 span，遵循 OpenTelemetry GenAI 语义约定。出问题要能在 30 秒内定位。

**Prompt 和配置版本化。** Prompt 进 git，走 review，有 diff 有回滚。线上跑的是哪个版本，必须能在 trace 里查到。

**灰度发布与回滚。** 新版本先小流量，看在线指标再放量。任何时候能一键回滚，且回滚要比发布更快。

**高危动作强制人工确认。** delete、send、pay、publish 四类是特权动作，必须硬确认加便捷回滚。背后是「最小代理权」原则：不只限制凭证能访问什么，还要限制 Agent 被允许自己决定什么。

**成本可见。** per-session 的 token 与费用要有看板。上下文越长成本越高、质量还越差，所以省 token 和提质量常常是同一件事。

**上下文工程而非堆 prompt。** 每一步都要决定哪些 token 值得占位置，而不是能塞就塞。

**工具接入走 MCP，Agent 协作走 A2A。** 不要给每个工具手写胶水代码。

**小模型分流加缓存降本。** 简单意图用小模型，重复前缀开 prompt caching。

**线上 case 回流成评估集。** 生产里的失败 case 人工标注后进 golden set，永久防止回归。**这是评估集唯一正确的增长方式。**

**长任务用异步架构。** 不要在一个 HTTP 请求里跑完，状态持久化，中间结果流式推送，断线可续。

**安全分层防御。** 权限阶梯、执行前钩子、操作系统级沙箱、人工中断、审计日志。提示注入至今仍是生产事故的头号来源，其中**间接注入**（恶意指令藏在 Agent 会读取的文档或网页里）最容易被忽视。

一个行业现实：Gartner 在 2025 年 6 月预测，到 2027 年底超过 40% 的 agentic AI 项目会被取消，主因是成本上升、价值不清、风险控制不足。**这恰恰说明 S3 和 S4 比 S2 更值钱** —— 会做 demo 的人很多，能把 Agent 做到可评估、可运维、成本可控的人很少。

---

## 5. 资源清单

**只列一手来源。** 二手博客的数字一律不可信，尤其是各种「2026 最佳框架对比」类的 SEO 内容，本计划核实时发现其中大量数据是编的。

### 必读（按阅读顺序，全部为 Anthropic 官方工程博客，括号内为实际发布日期）

| 文章 | 日期 | 用在 |
|---|---|---|
| [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) | 2024-12-19 | S2 开始前。五种工作流模式 + Agent 模式 |
| [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | 2025-09-29 | U1.5 |
| [Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) | 2025-09-11 | U2.2 |
| [Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval) | 2024-09-19 | U2.5 |
| [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system) | 2025-06-13 | U2.6 |
| [Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp) | 2025-11-04 | U2.7 |
| [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) | 2026-01-09 | **S3 整个阶段的方法论基础** |
| [Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) | 2025-11-26 | S4 |
| [Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing) | 2025-10-20 | U4.4 |
| [Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps) | 2026-03-24 | S4 |

完整列表见 [anthropic.com/engineering](https://www.anthropic.com/engineering)，每月看一次新增。

### 规范与协议

- [MCP 官方文档](https://modelcontextprotocol.io) 与 [官方 servers 仓库](https://github.com/modelcontextprotocol/servers)（9 万 star，大量可读实现）
- [A2A 协议](https://a2a-protocol.org)
- [OWASP GenAI Security Project](https://genai.owasp.org)

### 课程

| 资源 | 阶段 | 核实到的实际内容 |
|---|---|---|
| [CS50P](https://cs50.harvard.edu/python/) | S0 | 十周：函数与变量、条件、循环、异常、库、单元测试、文件 IO、正则、面向对象、其他，加期末项目。免费自学 |
| [Hugging Face AI Agents Course](https://huggingface.co/learn/agents-course/unit0/introduction) | S2 | 5 个单元（入门、Agent 基础、框架、用例、期末挑战）+ 三个加餐单元（函数调用微调、可观测性与评估、游戏 Agent）。单元 2 覆盖 smolagents、LangGraph、LlamaIndex。官方建议每单元一周约 3–4 小时。**认证完全免费** |
| [Learn Git Branching](https://learngitbranching.js.org/?locale=zh_CN) | U0.2 | 中文交互式练习 |

### 代码库（star 数为 2026-09-09 从 GitHub API 实测）

| 仓库 | star | 用途 |
|---|---|---|
| [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) | 90.2k | MCP server 实现范例 |
| [astral-sh/uv](https://github.com/astral-sh/uv) | 89.7k | Python 包管理 |
| [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | 41.3k | 编排框架，文档已迁至 docs.langchain.com |
| [langfuse/langfuse](https://github.com/langfuse/langfuse) | 34.4k | 可观测性与评估 |
| [openai/openai-agents-python](https://github.com/openai/openai-agents-python) | 29.3k | 轻量 Agent SDK |
| [huggingface/smolagents](https://github.com/huggingface/smolagents) | 29.3k | 极简实现，适合读源码 |
| [vercel/ai](https://github.com/vercel/ai) | 26.7k | 前端 AI 集成 |
| [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents) | 25.8k | 生产原则。**注意：最后更新 2025-09，按原则读、别按代码抄** |
| [a2aproject/A2A](https://github.com/a2aproject/A2A) | 25.7k | Agent 间协作协议 |
| [anthropics/claude-agent-sdk-python](https://github.com/anthropics/claude-agent-sdk-python) | 8.1k | Claude Code 同款能力 |

### 持续跟进

每周 1 小时，**选三个订阅就够**：Anthropic Engineering Blog、The Pragmatic Engineer、Latent Space 播客、阿里云与腾讯云开发者社区、GitHub Trending。

---

## 6. 进度追踪

| 周次 | 阶段 | 计划单元 | 实际完成 | 投入时长 | 卡点 |
|---|---|---|---|---|---|
| W1 | S0 | U0.1 U0.2 U0.3 |  |  |  |
| W2 | S0 | U0.4 U0.5 U0.6 |  |  |  |
| W3 | S0 | U0.7 U0.8 U0.9 |  |  |  |
| W4 | S0 | U0.10 M0 |  |  |  |
| W5 | S1 | U1.1 U1.2 U1.3 |  |  |  |
| W6 | S1 | U1.4 U1.5 |  |  |  |
| W7 | S1 | U1.6 U1.7 U1.8 M1 |  |  |  |
| W8 | S2 | U2.1 U2.2 |  |  |  |
| W9 | S2 | U2.3 U2.4 |  |  |  |
| W10 | S2 | U2.5 U2.6 |  |  |  |
| W11 | S2 | U2.7 U2.8 M2 |  |  |  |
| W12 | S3 | U3.1 U3.2 U3.3 |  |  |  |
| W13 | S3 | U3.4 U3.5 |  |  |  |
| W14 | S3 | U3.6 U3.7 |  |  |  |
| W15 | S3 | U3.8 M3 |  |  |  |
| W16 | S4 | U4.1 U4.2 |  |  |  |
| W17 | S4 | U4.3 U4.4 |  |  |  |
| W18 | S4 | U4.5 U4.6 |  |  |  |
| W19 | S4 | U4.7 U4.8 M4 |  |  |  |
| W20 | S5 | U5.1 U5.2 |  |  |  |
| W21 | S5 | U5.3 U5.4 |  |  |  |
| W22 | S5 | U5.5 U5.6 |  |  |  |
| W23 | S5 | U5.7 M5 |  |  |  |
| W24 | S6 | U6.1 U6.2 |  |  |  |
| W25 | S6 | U6.3 U6.4 |  |  |  |
| W26 | S6 | U6.5 |  |  |  |
| W27 | S6 | U6.6 M6 |  |  |  |

---

## 7. 常见坑

**跳过 S0 直接学 Agent。** 最常见也最致命。没有工程基础，你后面每个环境问题都会卡半天，写出来的代码也没人敢用。

**框架学了三个，循环没手写过一次。** U2.1 是整个 S2 的地基。跳过它，你永远只会调 API，不会 debug。

**评估集永远只有五条。** 参考 Anthropic 的建议，来自真实失败的 20 到 50 条是个好起点，而且必须正例负例都有。

**上下文能塞就塞。** 所有前沿模型在上下文变长时性能都会下降，且远在窗口填满前就开始。

**多 Agent 上瘾。** 大多数场景单 Agent 加好工具就够了。拆之前先用数据证明单 Agent 不行。

**用 AI 写完所有代码然后什么都不会。** S0 和 S1 的代码必须每行能讲。S2 之后可以放开用 AI 加速，但架构决策必须你自己做。

**只做不写。** 每周 4 小时复盘不是浪费，它是把「做过」变成「会讲」的唯一途径，而面试考的正好是后者。

**同时开三个项目。** 主线只有一个。S1 末尾定的那个题，做到 S6 结束。深度远比数量值钱。

---

## 8. 关于本文档的数据可靠性

写这份计划时核实过的内容，以及**主动删掉的内容**：

**已核实**（2026-09-09）

- 所有 GitHub star 数与最后更新时间，来自 GitHub API 实测
- 所有包版本，来自 npm registry 和 PyPI 官方接口
- Anthropic 工程博客的文章标题与发布日期，来自其官网列表页
- CS50P 与 Hugging Face Agents Course 的实际课程结构，来自各自官网
- MCP、A2A 的定位与治理结构，来自官方文档站
- CVE-2026-22708 与 CVE-2025-59532 的编号、日期、描述，来自 NIST NVD 数据库

**已删除**（初稿里有，核实后发现无法追溯到一手来源，全部移除）

- 「LangGraph 支撑 Klarna 8500 万用户」「比 CrewAI 低 47% token 成本」
- 「混合检索 MRR 66.4% vs 纯语义 56.7%」「RRF 达到 91% recall@10」
- 「MCP 下载量 9700 万」「A2A 有 150 家组织在生产使用」
- 各类「rerank 提升 15–30%」的通用数字

这些都来自搜索引擎里的 SEO 内容农场，看起来专业但查不到源头。**本计划的处理方式是：凡是要用数字支撑的判断，都改成让你在自己的项目上实测。** 别人的数字对你的语料和场景不成立，你自己测出来的才算数——这本身也是 S3 要教的东西。
