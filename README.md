# AI Agent 系统学习计划（零代码基础 → 生产级）

> 版本：2026-09-10 · 主线 37 周 · 每周 20 小时（其中 16 小时用在单元上）· 单元总时长 602 小时
> 路径：**A 主线**（AI 应用 / Agent 工程师 / 创业全栈）+ **B 扩展模块**（大厂平台基建，可激活）
> 目标：独立做 Agent 应用 + 看懂并参与 Agent 平台基建 + 能在业务里落地 + 能拿去面试 + 顺带能做网站/App/小程序

**这是什么**：一份从零代码基础开始、以 2026 年国内外真实招聘 JD 为依据倒推出来的 AI Agent 工程师学习路线。65 个单元，每个单元都有可运行的代码、实测过的输出和明确的完成判据。**不是资源清单，是一份照着做的施工图。**

**给谁**：想转行做 AI 应用 / Agent 工程师，愿意每周投入 20 小时、持续大半年的人。有编程基础的人可以从 S1 开始，S0 只做完成判据。

**怎么开始**：

```bash
# 1. 点右上角 Fork，把它变成你自己的仓库（进度勾选和笔记都会提交到你的 fork 里）
# 2. clone 你的 fork。本教程假设放在 ~/ai-agent-roadmap，放别处就把路径换成你的
git clone https://github.com/<你的用户名>/ai-agent-roadmap.git ~/ai-agent-roadmap
cd ~/ai-agent-roadmap
code .
```

然后读 [`从这里开始.md`](从这里开始.md)——VS Code 配置、每个单元的固定五步、前三天的具体清单。**Windows 用户先看 [U0.1 开头的 WSL2 说明](units/s0/U0.1-命令行与开发环境.md)。**

**路径选择**：主线走 A，[`扩展模块-B.md`](扩展模块-B.md) 是可激活的大厂平台基建扩展，里面写清了什么时候用什么数据来判断要不要开。

**七个阶段的项目怎么互相引用？** 见 [`项目结构.md`](项目结构.md)—— uv workspace、跨阶段依赖、csvstats 怎么承接。

**每个单元的详细拆解在 [`units/`](units/) 目录**，本文件是总览和索引。也可以看[网页版](https://yuyongyan29-dev.github.io/ai-agent-roadmap/)，带目录树和全文搜索。

| 阶段 | 文档 | 单元数 |
|---|---|---|
| **S0 工程地基** | [units/s0/](units/s0/README.md) | 12 |
| **S1 LLM 基础与上下文工程** | [units/s1/](units/s1/README.md) | 8 |
| **S2 Agent 核心** | [units/s2/](units/s2/README.md) | 8 |
| **S3 评估与可观测性** | [units/s3/](units/s3/README.md) | 8 |
| **S4 生产化** | [units/s4/](units/s4/README.md) | 9 |
| **S5 产品外壳** | [units/s5/](units/s5/README.md) | 7 |
| **S6 平台基建与面试** | [units/s6/](units/s6/README.md) | 6 |

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
├── 扩展模块-B.md      # 大厂平台基建扩展，可激活
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

| 阶段 | 主题 | 周次 | 单元时长 | 里程碑产出 |
|---|---|---|---|---|
| S0 | 工程地基 | W1–W6 | 94h | M0 带测试和 Docker 的 REST API |
| S1 | LLM 基础与上下文工程 | W7–W10 | 68h | M1 命令行 LLM 工具 + 需求规格化能力 |
| S2 | Agent 核心 | W11–W16 | 101h | M2 你自己场景的可用 Agent |
| S3 | 评估与可观测性 | W17–W21 | 84h | M3 给 M2 建完整 eval 与 trace |
| S4 | 生产化 | W22–W27 | 88h | M4 M2 真正上线，带灰度和 SLO |
| S5 | 产品外壳 | W28–W33 | 80h | M5 Web 前端 + 小程序入口 |
| S6 | 平台与基建 + 求职 | W34–W37 | 87h | M6 mini agent runtime + 作品集 + 简历 |
| **B** | **大厂平台基建扩展**（可选） | 追加 | +36h | 见 [`扩展模块-B.md`](扩展模块-B.md) |

**关于 37 周这个数字。** 上一版写的是 27 周，那是算错的：README 自己的节奏表是「输入 5 + 动手 11 + 复盘 4」，真正用在单元上的是每周 16 小时，而七个阶段合计 602 小时，602 ÷ 16 ≈ 37.6 周。**上一版从一开始就超配了 23%。** 排到 37 周意味着每周要挤出约 16.3 小时，比名义预算多 2%，靠复盘时间吸收。

用偏乐观的周期规划有两个后果：S0 就开始欠债；拖到 S3 那 84 小时时你会因为落后而想压缩它——**而 S3 是整份计划最不能压的部分。**

如果你实际每周能投 24 小时（20 小时单元 + 4 小时复盘），压到 **31 周**。两个数字不要混着用。

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

| 周次 | 阶段 | 计划单元（括号为课时） | 实际完成 | 投入时长 | 卡点 |
|---|---|---|---|---|---|
| W1 | S0 | U0.1(4) U0.2(6) U0.3(11) |  |  |  |
| W2 | S0 | U0.4(8) U0.5(6) |  |  |  |
| W3 | S0 | U0.6(8) U0.7(6) |  |  |  |
| W4 | S0 | U0.8(6) U0.9(6) |  |  |  |
| W5 | S0 | **U0.11 Redis(6)** **U0.12 Git worktree(8)** 起步 |  |  |  |
| W6 | S0 | U0.12 余 **U0.10 扩(13)** M0 |  |  |  |
| W7 | S1 | U1.1(6) U1.2(8) |  |  |  |
| W8 | S1 | U1.3(8) U1.4(8) |  |  |  |
| W9 | S1 | U1.5(10) U1.6(8) |  |  |  |
| W10 | S1 | U1.7(6) U1.8(6) **U1.9 需求发现(8)** M1 |  |  |  |
| W11 | S2 | U2.1(10) U2.2(8) |  |  |  |
| W12 | S2 | U2.3(8) U2.4(10) |  |  |  |
| W13 | S2 | **U2.5 扩(18)** |  |  |  |
| W14 | S2 | U2.6(10) U2.7(10) |  |  |  |
| W15 | S2 | **U2.9 Skill(5)** **U2.10 集成脏活(4)** U2.8 起步 |  |  |  |
| W16 | S2 | **U2.8 扩(18)** 余 M2 |  |  |  |
| W17 | S3 | U3.1(4) U3.2(12) |  |  |  |
| W18 | S3 | U3.3(8) **U3.5 扩(16)** 起步 |  |  |  |
| W19 | S3 | U3.4(10) U3.5 余 |  |  |  |
| W20 | S3 | U3.6(10) U3.7(12) 起步 |  |  |  |
| W21 | S3 | U3.7 余 U3.8(12) M3 |  |  |  |
| W22 | S4 | U4.1(6) U4.2(10) |  |  |  |
| W23 | S4 | **U4.3 扩(16)** |  |  |  |
| W24 | S4 | U4.4(14) |  |  |  |
| W25 | S4 | U4.5(10) U4.6(10) 起步 |  |  |  |
| W26 | S4 | U4.6 余 **U4.0 Linux(4)** U4.7(12) 起步 |  |  |  |
| W27 | S4 | U4.7 余 **U4.8 扩(10)** M4 |  |  |  |
| W28 | S5 | U5.1(10) |  |  |  |
| W29 | S5 | U5.2(14) |  |  |  |
| W30 | S5 | U5.3(12) |  |  |  |
| W31 | S5 | U5.4(12) |  |  |  |
| W32 | S5 | U5.5(10) U5.6(14) 起步 |  |  |  |
| W33 | S5 | U5.6 余 U5.7(8) M5 |  |  |  |
| W34 | S6 | U6.1(10) U6.2(14) 起步 |  |  |  |
| W35 | S6 | U6.2 余 U6.3(12) |  |  |  |
| W36 | S6 | U6.4(10) U6.5(20) 起步 |  |  |  |
| W37 | S6 | U6.5 余 **U6.6 扩(21)** M6 |  |  |  |

**加粗的是本次新增或扩容的单元。** 七个新单元：U0.11 Redis、U0.12 Git 分支与 worktree、U1.9 需求发现、U2.9 Skill 与 Plugin、U2.10 企业系统集成、U4.0 Linux 运维，以及可选的 [B 扩展模块](扩展模块-B.md)。八处扩容：U0.3 加复杂度分析、U0.10 加 Cursor 实操、U2.5 加语料治理、U2.8 加框架词汇映射、U3.5 加归因盲测、U4.3 加消息队列、U4.8 加压测、U6.6 加简历与投递。

**算法练习不占单元时间。** 从 W12 起，每周复盘的 4 小时里切 20 分钟做 1 题，20 周共 20 题，覆盖双指针、哈希、二分、树遍历、简单 DP 五类。理由见下面的「关于算法笔试」。

---

## 7. 关于算法笔试：为什么只给 6 小时

这一条是本次调研里争议最大的，我把证据两边都摆出来。

**支持补的证据**：后端工程师通用角度，数据结构与算法出现在 3/10 条 JD 里。海外有两个面试流程点，Cursor 的初轮编码面试禁用 AI。

**不支持大改的证据**：本次核验的 84 条 2026 年 JD 里，大厂 26 条 + 创业公司 21 条 + 海外 14 条 + 软技能 13 条，**共 74 条，算法与数据结构关键词出现 0 次**。唯一能直接回答「面试到底考不考」的是面经角度，但它没通过时效核验——标称 13 条实际是 16 个链接且无一条是 JD。剩下 2 份可核验的一手面经里，字节 AI 应用开发一面楼主在评论区明确回复「无手撕」，蚂蚁 agent 开发一面 29 道题里也没有。

**n=2 证明不了「不考」，3/10 也证明不了「必考」。两边证据都薄，所以投 20 小时是过度反应。**

**处置：默认给 6 小时的防猝死版，做成可切换的开关。**

复杂度分析补进 U0.3，1 小时。讲 list/dict/set/tuple 选型却不讲 O(1) 和 O(n)，本来就缺一块。

每周复盘的 4 小时里切 20 分钟做 1 题，W10 起共 20 题，覆盖双指针、哈希、二分、树遍历、简单 DP 五类。用 Python 写，每题写清思路和复杂度。**分摊约 7 小时，不占单元时间。**

禁 AI 的 60 分钟手写 agent loop，做三次，3 小时。**这条有确切证据**（Cursor 那份 JD 的初轮编码面试禁用 AI），而且素材现成——U2.1 那 200 行。计划从 S2 起明确「可以放开用 AI 加速」，这对做事是对的，但对禁 AI 的初轮编码面试是危险的。

**什么时候升级成完整版**：只有当你确定要投国内大厂校招，或者投通用后端社招时，才扩到 40 题加 15 道后端八股，约 20 小时。届时那 20 小时是合理的。

---

## 8. 常见坑

**跳过 S0 直接学 Agent。** 最常见也最致命。没有工程基础，你后面每个环境问题都会卡半天，写出来的代码也没人敢用。

**框架学了三个，循环没手写过一次。** U2.1 是整个 S2 的地基。跳过它，你永远只会调 API，不会 debug。

**评估集永远只有五条。** 参考 Anthropic 的建议，来自真实失败的 20 到 50 条是个好起点，而且必须正例负例都有。

**上下文能塞就塞。** 所有前沿模型在上下文变长时性能都会下降，且远在窗口填满前就开始。

**多 Agent 上瘾。** 大多数场景单 Agent 加好工具就够了。拆之前先用数据证明单 Agent 不行。

**用 AI 写完所有代码然后什么都不会。** S0 和 S1 的代码必须每行能讲。S2 之后可以放开用 AI 加速，但架构决策必须你自己做。

**只做不写。** 每周 4 小时复盘不是浪费，它是把「做过」变成「会讲」的唯一途径，而面试考的正好是后者。

**同时开三个项目。** 主线只有一个。S1 末尾定的那个题，做到 S6 结束。深度远比数量值钱。

---

## 9. 关于本文档的数据可靠性

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

---

## 10. 许可与贡献

- 文档（所有 `.md`）采用 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans)：可以自由转载、改编、用于教学，注明来源即可。
- 代码片段与脚本（`scripts/`、文档中的代码块）采用 [MIT](LICENSE)。
- 发现版本号过期、链接失效、数据存疑或步骤跑不通，请按 [`CONTRIBUTING.md`](CONTRIBUTING.md) 提 issue 或 PR。**附一手来源**是唯一的硬要求。
