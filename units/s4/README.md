# Stage 4 · 生产化（W22–W28，90 小时）

**目标**：让 M2 的 Agent 从「我能跑」变成「别人在用，出事我知道，改坏能回滚」。

---

## 单元列表

按学习顺序排。U4.0 和 U4.9 的编号不按顺序，因为它们是后来补进来的「地基」：前者讲机器，后者讲机器周围的基础设施。

| 单元 | 时长 | 你会做出什么 |
|---|---|---|
| [U4.1 12-Factor 自查](U4.1-12Factor自查.md) | 6h | 一张差距表，就是后面单元的待办清单 |
| [U4.2 状态与持久化](U4.2-状态与持久化.md) | 10h | kill -9 后能续跑，副作用不重复 |
| [U4.3 长任务架构](U4.3-长任务架构.md) | 12h | 异步 + SSE，断线重连能补齐事件 |
| [U4.4 安全与权限](U4.4-安全与权限.md) | 14h | 10 个攻击样本全部失效 |
| [U4.5 成本治理](U4.5-成本治理.md) | 10h | 成本降 40%，评估分掉不到 2% |
| [U4.6 灰度与回滚](U4.6-灰度与回滚.md) | 10h | 两版本同时在线，配置回滚 2 分钟内 |
| [U4.0 Linux 服务器与线上排查](U4.0-Linux服务器与线上排查.md) | 4h | 一台真实服务器，systemd、nginx、排查五件套 |
| [U4.9 基础设施实操](U4.9-基础设施实操.md) | 8h | **镜像仓库、Caddy HTTPS、数据库备份与恢复演练、对象存储、生产 Redis、push 即上线** |
| [U4.7 部署上线](U4.7-部署上线.md) | 10h | 真实可访问的地址 + 手机告警 |
| [U4.8 SLO 与 Runbook](U4.8-SLO与Runbook.md) | 6h | 三种故障照着走就能处理 |

**M4 里程碑**：Agent 真的上线了，有灰度、有告警、有 SLO、有成本控制、有备份。

---

## 必读

- [humanlayer/12-factor-agents](https://github.com/humanlayer/12-factor-agents)（2.6 万 star）。**注意最后更新是 2025 年 9 月，按原则读、别按代码抄。**
- Anthropic《[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)》（2025-11-26）
- Anthropic《[Beyond permission prompts](https://www.anthropic.com/engineering/claude-code-sandboxing)》（2025-10-20）
- Anthropic《[How we built Claude Code auto mode](https://www.anthropic.com/engineering/claude-code-auto-mode)》（2026-03-25）
- [OWASP GenAI Security Project](https://genai.owasp.org)

---

## 这一阶段的三条主线

**主线一：让它不丢东西。** U4.2 的断点续跑和幂等、U4.3 的异步和事件持久化、U4.9 的备份与恢复演练。核心问题是「进程随时会死、磁盘随时会坏，怎么保证不丢不重」。

**主线二：让它不出事。** U4.4 的安全、U4.6 的灰度回滚、U4.8 的 SLO 和 Runbook。核心问题是「出问题时怎么快速发现和止损」。

**主线三：让它真的在线上。** U4.0 一台机器、U4.9 机器周围的基础设施、U4.7 应用的生产配置和发布流水线。这三个单元是「部署」这件事的完整链条：**镜像怎么到服务器、HTTPS 从哪来、数据库怎么备份、文件存哪、push 之后发生什么**，每一步都亲手做过。

U4.5 的成本治理是这三条主线之外的，但它**完全依赖 S3 的评估体系**——没有评估，你不敢做任何优化。

---

## U4.4 的时间不要压缩

它是整个 S4 里唯一一个「不做会出事故」而不是「不做会体验差」的单元。

14 小时里，**建议至少 4 小时花在「攻击自己」上**。不知道能被怎么攻破，就不知道该防什么。

两个真实的 CVE（Cursor 的白名单绕过、Codex CLI 的沙箱边界被模型输出重定义）都不是「模型作恶」，而是**工程实现的边界搞错了**。写这两个工具的都是顶尖团队——你也会犯类似的错。
