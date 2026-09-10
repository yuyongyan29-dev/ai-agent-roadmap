# 本地教学实验核验

核验日期：2026-09-10。环境：macOS arm64、Python 3.14.6；临时虚拟环境安装 Locust 2.46.5、Pika 1.4.4、Langfuse 4.15.2。没有调用真实模型、修改正式服务或启动外部基础设施。

## Trace SDK

在仓库根目录运行（`python` 是上述虚拟环境的解释器）：

```bash
python examples/production-labs/tracing_smoke.py
```

实际输出：

```text
spans=4 one_trace=True parent_links=True
export=in-memory model=mock remote_ingestion=not-tested
```

断言验证 4 个 observation、同一 trace ID、轮次与工具/模型的父子关系。使用 SDK 的内存 exporter，没有测试网络导出、认证、评分接收或 Langfuse 界面。示例中的保修数据是实验 fixture，不是产品事实。

## Locust 六组 smoke

每组命令如下，分别替换 `LAB_PATH=/health`、`/db`、`/agent`；基线和带 `--indexed` 的服务各跑三组。`PREFIX` 指向本次临时目录中的独立 CSV 前缀。

```bash
python examples/production-labs/load_service.py --port 18765
LAB_PATH=/health python -m locust -f examples/production-labs/locustfile.py --headless --host http://127.0.0.1:18765 -u 8 -r 8 -t 5s --csv "$PREFIX" --only-summary
```

环境相同、单机服务与压测器同机运行。数据为 20000 行 SQLite 实验数据，请求固定查最后一个 key；每用户请求后等 20ms。mock 模型两个槽位、处理延迟 40ms、等待槽位超时 50ms，均为人工实验参数。

以下逐项摘自生成的 `*_stats.csv`。Locust 在运行中定期写 CSV；短跑退出时读取到的快照不一定包含最后一瞬间全部请求，因而不把请求数除以设置的 5 秒计算 QPS。不同轮次样本数不相同，未做正式暖机或统计显著性分析。

| 索引 | 端点 | Request Count | Failure Count | Requests/s | P50 ms | P95 ms | 退出码 |
|---|---|---:|---:|---:|---:|---:|---:|
| 无 | `/health` | 592 | 0 | 295.19913507508767 | 3 | 6 | 0 |
| 无 | `/db` | 1096 | 0 | 274.5568472051531 | 5 | 7 | 0 |
| 无 | `/agent` | 360 | 176 | 90.26732277465216 | 63 | 94 | 1 |
| 有 | `/health` | 1136 | 0 | 284.8740530463824 | 4 | 6 | 0 |
| 有 | `/db` | 1120 | 0 | 280.7897056496787 | 5 | 7 | 0 |
| 有 | `/agent` | 358 | 175 | 89.64410088997494 | 63 | 95 | 1 |

`/agent` 的 429 是有意保留的 mock 并发限额失败，并非测试通过率。requests/s 包含失败请求；这一实验没有得出成功任务容量。

索引改动前后 HTTP P95 没有明显改善，不能声称性能优化成功。这里只证明脚本能依次触达三层、保留失败、输出统计，并能对同一负载做单项修改前后对照。

另在默认端口 8765 分别启动两种模式，请求 `/agent`，实际输出与验证：

```text
local-mock port=8765 indexed=False plan=SCAN items
agent_response=200 fields_present=True
local-mock port=8765 indexed=True plan=SEARCH items USING INDEX item_key_idx (item_key=?)
agent_response=200 fields_present=True
```

响应中 `mode=local-mock`、`value=value-19999`、`indexed` 均符合预期，包含 `db_ms`、`model_wait_ms`、`model_ms`。这两次单请求验证说明模型槽有空闲时可以成功，不能替代持续负载测量。

## RabbitMQ 的已验与未验

```bash
docker compose -p roadmap-rabbit-lab -f examples/production-labs/rabbit.compose.yaml config --quiet
python examples/production-labs/rabbit_lab.py --help
```

均退出 0。Compose 仅检查配置解析，不拉取镜像，也不证明 broker 可以启动。脚本入口可解析；在临时 SQLite 中对同一 task ID 连续调用 `effect_once`，实际输出：

```text
first= True duplicate= False
```

这只验证本地唯一键与事务；没有验证 RabbitMQ 的发布、confirm、ack、重投、死信、积压或 PG 对照。Docker daemon 检查实际返回：

```text
failed to connect to the docker API ... docker.sock: connect: no such file or directory
```

因此 U4.3 的完整 broker 崩溃演练仍需学习者在具备环境后完成，不能用本地 SQLite 验证代替。没有验证任何“exactly-once”保证。

## 复现和结束

从 `~/ai-agent-roadmap` 建立学习用虚拟环境，并安装本目录 `requirements.txt`；按 U3.5、U4.3、U4.8 的步骤运行。普通服务实验用 Ctrl+C 结束，临时 SQLite 随服务退出清理。RabbitMQ 实验只操作 `roadmap-rabbit-lab` Compose 项目；先归档自己的记录，再删除该项目的实验卷和效果数据库。

本次核验产生的服务器进程、临时数据库和 CSV 已清理；表中保留实际统计摘录。临时 Python 环境不属于仓库依赖，不需要提交。
