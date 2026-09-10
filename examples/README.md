# 实操示例

这些是单元里的小型参考程序，用来先跑通一个明确的边界，再由你和 coding agent 接到自己的主线项目。固定数据与 fake 模型只验证对应逻辑，不能证明真实模型质量或线上容量。

在仓库根目录运行，详细步骤与验收见对应单元：

| 示例 | 对应单元 | 本地可验证什么 |
|---|---|---|
| [Skill / Plugin 文件与夹具](skill-plugin-lab/verify.py) | [U2.9](../units/s2/U2.9-Skill与Plugin.md) | 两个 Skill 的结构、检索回归比较、异常输入 |
| [SaaS 故障实验](saas-integration-lab/verify.py) | [U2.10](../units/s2/U2.10-企业系统集成.md) | 授权状态、轮转、分页限流、验签、去重、检查点 |
| [Qdrant 生命周期](rag-lifecycle/README.md) | [U2.5](../units/s2/U2.5-RAG与混合检索.md) | 本地固定向量、权限过滤、版本切换、删除 |
| [LangGraph 恢复](framework-recovery/README.md) | [U2.8](../units/s2/U2.8-框架横评.md) | 跨进程确认、拒绝、写入后崩溃与幂等恢复 |
| [Trace、队列、压测的验证记录](production-labs/VERIFICATION.md) | [U3.5](../units/s3/U3.5-Trace与可观测性.md)、[U4.3](../units/s4/U4.3-长任务架构.md)、[U4.8](../units/s4/U4.8-SLO与Runbook.md) | 内存 trace、SQLite 唯一效果、本地分层 HTTP 压测 |

以下四条不需要真实模型密钥。前两条只用 Python 标准库，后两条由 `uv` 按脚本声明安装已固定版本的依赖：

```bash
python3 examples/skill-plugin-lab/verify.py
python3 examples/saas-integration-lab/verify.py
uv run examples/rag-lifecycle/qdrant_smoke.py
uv run examples/framework-recovery/langgraph_smoke.py
```

产线实验所需依赖写在 [requirements.txt](production-labs/requirements.txt)。真实 RabbitMQ、Langfuse 平台、Slack 回调与模型调用的验证条件各不相同，先按单元准备环境，再分别记录本地通过、实连通过和未验证项。
