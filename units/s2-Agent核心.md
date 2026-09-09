# Stage 2 · Agent 核心（W7–W10，80h）

**第一天先做一件事**：确认 `s2-agent/PROJECT.md` 里的选题定下来了。后面四个阶段全部围绕它。

**必读，在 U2.1 之前读完**：Anthropic《[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)》（2024-12-19）。它定义了五种工作流模式（Prompt Chaining、Routing、Parallelization、Orchestrator-Workers、Evaluator-Optimizer）和一种 Agent 模式，并给出一条贯穿全文的建议：**从最简单的方案开始，只在必要时增加复杂度。工作流适合路径确定的任务，Agent 适合需要模型自主决策的开放场景。**

大多数人做 Agent 的第一个错误，就是本该用工作流的地方用了 Agent。

---

## U2.1 手写 Agent 循环（10h）

**目标**：**不用任何框架**，200 行以内实现一个能用的 Agent。这是整个 S2 的地基，跳过它你后面永远在调 API 而不是在做工程。

**具体做什么**

1. 理解 Agent 的本质就是一个循环：
   ```
   while 未完成 and 轮次 < 上限:
       响应 = 调模型(系统提示, 工具定义, 消息历史)
       if 响应包含工具调用:
           结果 = 执行工具(...)
           消息历史.append(工具调用); 消息历史.append(结果)
       else:
           return 响应.文本
   ```
2. 定义三个工具，用你项目里真实需要的，比如「搜索」「读文件」「查数据库」。
3. 实现工具注册表：一个 dict，把工具名映射到函数，同时能生成给模型看的 JSON schema。
4. 实现执行器：解析模型返回的工具调用，找到函数，传参，捕获异常，把结果（包括错误）转成字符串回填。
5. **必须加的护栏**：最大轮次限制、单次工具超时、总 token 预算上限。没有这三样，一个死循环能烧掉你几百块。
6. 加上详细日志：每一轮打印模型想调什么工具、传了什么参数、返回了什么。**这是你后面 debug 的唯一依靠。**

**产出**：`s2-agent/core/loop.py`（不超过 200 行）

**完成判据**：用三个工具完成一个需要至少四步的真实任务。**并且你能对着代码逐行讲清楚每一行在干什么。**

**常见卡点**：工具调用的消息格式各家不同，OpenAI 用 `tool_calls`，Anthropic 用 `content` 里的 `tool_use` block。先固定用一家做通，再抽象。

---

## U2.2 工具设计（8h）

**目标**：让模型用对工具。**Agent 的失败有很大比例不是模型笨，是工具设计得烂。**

**必读**：Anthropic《[Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents)》（2025-09-11）。

**具体做什么**

1. 工具描述怎么写：说清楚「什么时候该用它」比说清楚「它做什么」更重要。加一句「什么时候不该用它」效果往往更好。
2. 参数设计：用枚举而不是自由字符串、必填项越少越好、给默认值、参数名要自解释。
3. **返回值设计是最被低估的一环**。返回太少模型不知道下一步做什么，返回太多污染上下文。原则是：返回模型做决策需要的信息，而不是全部数据。一个 500 行的查询结果应该返回「找到 500 条，前 5 条是……，可用 offset 翻页」。
4. 错误返回要可行动：不要返回 `Error: 500`，要返回「查询失败，因为日期格式应为 YYYY-MM-DD，你传的是 2026/1/1」。
5. **工具太多怎么办**：超过 15 到 20 个工具，模型的选择准确率会明显下降。三种解法——按场景分组、动态加载当前任务相关的子集、用一个「工具搜索」的元工具。
6. 幂等性：可能被重复调用的工具必须幂等。「发邮件」不幂等，要么加去重键，要么设计成需要确认。
7. **做对照实验**：同一个工具写两版描述，跑 20 个任务，统计调用准确率。

**产出**：`s2-agent/tools/`（8 个工具）、`s2-agent/eval/tool_desc_ab.md`

**完成判据**：一份对照实验数据，说明工具描述的某个具体写法把准确率从 X 提到了 Y。

---

## U2.3 规划与反思（8h）

**目标**：知道三种模式各适合什么，并能用数据支持你的选择。

**具体做什么**

1. **ReAct**（U2.1 已实现）：想一步做一步，灵活但容易跑偏、步数多。
2. **Plan-and-Execute**：先让模型输出完整计划，再逐步执行，每步后检查是否需要改计划。步数可控，但计划错了全盘错。
3. **Reflexion / Evaluator-Optimizer**：生成结果后让另一次调用来评价，不合格就带着评价重做。质量高，成本翻倍。
4. 三种各实现一遍，在同一组 10 个任务上跑，记录：成功率、平均步数、平均成本、平均耗时。
5. 理解一个关键判断：**你的任务路径是不是确定的**。确定的用工作流（if/else 或 DAG），不确定的才用 Agent。大多数业务任务其实是确定的。

**产出**：`s2-agent/patterns/{react,plan_execute,reflexion}.py`、`s2-agent/eval/pattern_compare.md`

**完成判据**：一张四指标对比表，加一句结论——你的项目用哪种、为什么。

---

## U2.4 记忆系统（10h）

**目标**：Agent 能跨会话记住东西，且记住的是对的东西。

**具体做什么**

1. 分清三种记忆，它们的存储和检索方式完全不同：
   - **短期**：当前会话的消息历史，存在内存或 Redis，随会话结束消失
   - **工作记忆**：当前任务的中间状态（已完成哪几步、拿到了什么），存在任务状态里
   - **长期**：跨会话的用户偏好和事实，存数据库，需要检索
2. 实现长期记忆的写入：**不是把所有对话都存下来**，而是让模型判断「这句话里有值得长期记住的事实吗」，有才抽取成结构化条目存入。
3. 实现检索：新会话开始时，根据当前话题检索相关记忆，注入系统提示。
4. **处理事实冲突**：用户上周说喜欢 A，这周说喜欢 B。记忆条目要带时间戳和来源，检索时新的覆盖旧的，并保留历史。
5. **处理时效性**：「项目截止日期是 3 月 1 日」这条记忆在 3 月 2 日就该失效。给记忆加有效期或时效标记。
6. 加遗忘机制：长期不被检索到的记忆降权或归档，否则记忆库会无限膨胀并稀释检索质量。

**产出**：`s2-agent/memory/`

**完成判据**：跨会话测试——第一次会话说「我只做家电类目」，隔天新会话里 Agent 自动只搜家电；再说「我现在也做家居了」，之后两个类目都覆盖。

---

## U2.5 RAG 与混合检索（12h）

**目标**：搭出一条能用的检索管线，并用数据证明每一步优化的价值。

**必读**：Anthropic《[Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)》（2024-09-19），它讲清楚了为什么单纯的向量检索不够，以及给每个 chunk 加上下文摘要能带来什么。

**具体做什么**

1. **准备语料**：50 篇以上你项目真实需要的文档。
2. **切分**：试三种策略——固定长度加重叠、按标题结构切、按语义边界切。切分是 RAG 里影响最大也最被忽视的一环。
3. **嵌入**：选一个中文效果好的 embedding 模型（BGE 系列或各云厂商的），批量嵌入，存进 Postgres 的 `pgvector` 扩展。
4. **建两路召回**：
   - 向量检索：`pgvector` 的余弦相似度
   - 关键词检索：Postgres 全文检索，中文需要装分词扩展（`zhparser` 或 `pg_jieba`）
5. **融合**：用 RRF（Reciprocal Rank Fusion）把两路结果合并。RRF 的好处是不需要归一化两边的分数，实现简单。
6. **重排**：召回 top-50 后用 cross-encoder 重排到 top-5。可以用云端的 rerank API（阿里、Cohere、Jina 都有）或本地跑 BGE-reranker。
7. **量化每一步**：准备 20 组「问题 + 正确答案所在的文档」，测每一版配置的召回率和 MRR。**必须自己测，不要信任何博客上的数字，你的语料和别人的不一样。**

**产出**：`s2-agent/rag/`、`s2-agent/eval/retrieval_bench.md`

**完成判据**：一张递进的对比表——纯向量 / 加 BM25 / 加 RRF / 加 rerank 四档配置在你自己语料上的召回率，每一步的提升幅度是多少。

**常见卡点**：中文全文检索需要额外的分词扩展，Docker 镜像用 `pgvector/pgvector` 再自己加分词，或者先用简单的 `LIKE` 匹配跑通流程再优化。

---

## U2.6 多 Agent 编排（10h）

**目标**：知道什么时候该拆，更重要的是知道什么时候不该拆。

**必读**：Anthropic《[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)》（2025-06-13）。它讲了 orchestrator 和 subagent 的分工、上下文隔离的价值，以及多 Agent 的成本代价。

**具体做什么**

1. 实现 **Orchestrator-Worker**：主 Agent 拆任务，派给若干子 Agent 并行做，收集结果后汇总。
2. 实现 **Handoff**：一个 Agent 判断这事该另一个 Agent 管，把控制权和上下文交出去。
3. 理解**上下文隔离**为什么是多 Agent 最大的价值：子 Agent 只看到自己那部分上下文，不会被主线的噪音污染，也不会把自己的探索过程塞进主上下文。
4. **理解代价**：多 Agent 的 token 消耗通常是单 Agent 的数倍，因为每个子 Agent 都要重新建立上下文。并行还带来协调、错误传播、结果冲突的问题。
5. **做实证**：把你项目里一个复杂子任务拆成子 Agent，和不拆的版本在同一组任务上对比质量、成本、耗时。
6. **诚实地下结论**：如果拆了没更好，就写清楚为什么。**大多数项目单 Agent 加好工具就够了，这个结论本身就是有价值的工程判断。**

**产出**：`s2-agent/multi/`、`s2-agent/eval/multi_vs_single.md`

**完成判据**：一份带数据的对比，和一个明确的决定——你的项目用不用多 Agent。

---

## U2.7 MCP 实战（10h）

**目标**：能写 MCP server，也能在自己的 Agent 里当 MCP client。这是 2026 年 Agent 接工具的事实标准。

**参考**：[MCP 官方文档](https://modelcontextprotocol.io)，最新规范版本见文档站；[官方 servers 仓库](https://github.com/modelcontextprotocol/servers) 有大量可读的实现范例。

**具体做什么**

1. 先当用户：在 Claude Code 或 Claude Desktop 里接几个现成的 MCP server（文件系统、GitHub、数据库），体会它们怎么被调用。
2. 理解三种原语的区别：
   - **Tools**：模型可以主动调用的函数
   - **Resources**：可被读取的数据（文件、记录），由客户端决定何时读
   - **Prompts**：预置的提示模板，通常由用户主动触发
3. 理解传输方式：`stdio`（本地进程，最简单）和 HTTP 流式（远程服务）。先用 stdio。
4. `uv add mcp`，用官方 Python SDK 写你自己的 server，暴露 3 个工具——**就用你 U2.2 写的那三个**。
5. 在 Claude Code 里接入它，验证能被调用。
6. 再写一个 MCP client 接进你自己的 Agent，让 U2.1 的循环通过 MCP 拿工具，而不是硬编码。
7. 读一读 Anthropic《[Code execution with MCP](https://www.anthropic.com/engineering/code-execution-with-mcp)》（2025-11-04），理解工具太多时用代码执行代替逐个工具调用的思路。

**产出**：`s2-agent/mcp_server/`、`s2-agent/mcp_client.py`

**完成判据**：你写的这一个 MCP server，能同时被 Claude Code 和你自己的 Agent 使用，不改一行代码。

---

## U2.8 框架横评（12h）

**目标**：知道框架替你做了什么、代价是什么，然后为主线项目选一个。**不要在选型上纠结超过这一个单元。**

**候选**（2026 年 9 月的实际状态）

| 框架 | 语言 | 特点 |
|---|---|---|
| [LangGraph](https://docs.langchain.com/oss/python/langgraph/overview) | Python / JS | 显式状态图，持久化、断点续跑、人工介入、流式都是一等公民。生态和文档最全 |
| [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) | Python / JS | 抽象轻，核心概念只有 agent、tool、handoff、guardrail、session，自带 tracing |
| [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk-python) | Python / TS | Claude Code 同款能力的可编程版本，MCP 集成最深，适合需要文件和命令行操作的 Agent |
| [smolagents](https://github.com/huggingface/smolagents) | Python | 极简，代码量小到能读完，适合学习原理 |

**具体做什么**

1. 用同一个任务（选你项目里的一个真实场景），在三个框架里各实现一遍。
2. 每次实现后回答同样六个问题：状态存在哪里、怎么持久化、怎么流式输出、工具出错怎么恢复、怎么接可观测性、代码多少行。
3. 特别关注**持久化和断点续跑**，这是 S4 生产化的硬需求。跑到一半杀掉进程，看哪个框架能续上。
4. 读一读 smolagents 的源码，它足够小，能让你看清框架到底做了什么。

**产出**：`s2-agent/frameworks/{langgraph,openai_sdk,claude_sdk}/`、`s2-agent/FRAMEWORK_CHOICE.md`

**完成判据**：一份带代码和六项对比的文档，最后一段写明「本项目选 X，因为……，放弃 Y 是因为……」。

---

## M2 里程碑

**交付物**：主线 Agent 的第一个可用版本，你自己每周真的会用它。

**验收清单**

- [ ] 能完成 `PROJECT.md` 里定义的核心任务，成功率你心里有数
- [ ] 至少 5 个工具，其中 3 个通过 MCP 暴露
- [ ] 有短期和长期记忆
- [ ] 有 RAG 检索，且检索质量有量化数据
- [ ] 有轮次、超时、token 预算三重护栏
- [ ] 全程日志，出错能定位到具体哪一轮哪个工具
- [ ] README 有架构图和一次完整运行的示例

**下一阶段预告**：S3 会让你回答一个残酷的问题——**你怎么知道它做得好？** 现在你大概率答不上来，这很正常。
