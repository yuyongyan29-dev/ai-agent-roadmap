# LangGraph 恢复最小例

从仓库根目录运行：

```bash
uv run examples/framework-recovery/langgraph_smoke.py
```

2026-09-10 已实跑，`langgraph==1.2.11`、`langgraph-checkpoint-sqlite==3.1.1`。每次操作由独立子进程执行；三个 PASS 验证跨进程批准、拒绝，以及业务回执提交后突然退出、再次恢复的结果。

示例不调用模型或外部服务。SQLite checkpoint 与业务回执分开保存，后者通过唯一业务键让重试不会产生第二份回执。故障注入采用 `os._exit(70)`，临时目录由父进程清理。

它不验证并发恢复、远程工具幂等、审批人认证、草稿变更导致审批失效，也不执行跨框架 checkpoint 转换。按 U2.8 的实验合同，将这些边界接到你自己的两个候选上；不能把三个 PASS 当成整个框架横评完成。

API 来源：[LangGraph Interrupts](https://docs.langchain.com/oss/python/langgraph/interrupts)、[Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)。
