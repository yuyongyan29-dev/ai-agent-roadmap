# RAG 生命周期最小例

从仓库根目录运行：

```bash
uv run examples/rag-lifecycle/qdrant_smoke.py
```

2026-09-10 已实跑，`qdrant-client==1.19.0`。五条 PASS 分别验证重复入库、身份与权限过滤、版本切换、所有版本删除、关闭客户端后重新打开索引。运行只创建自动清理的临时本地索引，不请求模型或数据库服务。

固定三维向量只为验证过滤与生命周期；`active_versions` 和 `allowed_docs` 模拟可信目录与权限查询。示例不提供身份认证、目录持久化、内容散列校验、并发版本切换和生产清理任务。真实项目按 U2.5 步骤 8 补齐这些责任，再用同一批真实向量做检索对照。

API 来源：[Qdrant Python client](https://github.com/qdrant/qdrant-client)、[Points](https://qdrant.tech/documentation/manage-data/points/)、[Filtering](https://qdrant.tech/documentation/search/filtering/)。
