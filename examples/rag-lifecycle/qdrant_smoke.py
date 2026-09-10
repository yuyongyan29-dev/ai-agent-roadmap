# /// script
# requires-python = ">=3.11"
# dependencies = ["qdrant-client==1.19.0"]
# ///
"""离线验证过滤、幂等写入、版本切换和删除；固定向量不用于评测语义质量。"""
from tempfile import TemporaryDirectory
from uuid import NAMESPACE_URL, uuid5

from qdrant_client import QdrantClient, models


COLLECTION = "rag_lifecycle_demo"


def exact(key, value):
    return models.FieldCondition(key=key, match=models.MatchValue(value=value))


def document_filter(tenant, doc_id):
    return models.Filter(must=[exact("tenant_id", tenant), exact("doc_id", doc_id)])


def write_version(client, tenant, doc_id, version, text, acl):
    # chunk 序号只在不可变的同一版本内稳定；真实数据还需校验内容散列。
    point_id = str(uuid5(NAMESPACE_URL, f"{tenant}/{doc_id}/{version}/0"))
    client.upsert(
        COLLECTION,
        points=[models.PointStruct(
            id=point_id, vector=[1.0, 0.0, 0.0],
            payload={"tenant_id": tenant, "doc_id": doc_id, "version": version,
                     "acl": acl, "text": text, "page": 1},
        )],
        wait=True,
    )


def retrieve(client, tenant, principal, allowed_docs, active_versions):
    # tenant、principal 和 allowed_docs 来自可信身份/权限服务，不来自模型参数。
    # 演示只查询权限服务已经授权的文档；版本清单是本地内存模拟的权威目录。
    active = [models.Filter(must=[exact("doc_id", doc_id), exact("version", version)])
              for (owner, doc_id), version in active_versions.items()
              if owner == tenant and doc_id in allowed_docs]
    if not active:
        return []
    result = client.query_points(
        COLLECTION,
        query=[1.0, 0.0, 0.0], limit=5,
        query_filter=models.Filter(
            must=[exact("tenant_id", tenant), exact("acl", principal)], should=active,
        ),
        with_payload=True,
    )
    return [point.payload["text"] for point in result.points]


def main():
    with TemporaryDirectory(prefix="rag-lifecycle-") as directory:
        client = QdrantClient(path=directory)
        client.create_collection(
            COLLECTION, vectors_config=models.VectorParams(size=3, distance=models.Distance.COSINE),
        )
        active = {("team_a", "policy"): "v1", ("team_b", "policy"): "v1"}
        write_version(client, "team_a", "policy", "v1", "policy v1", ["alice"])
        write_version(client, "team_a", "policy", "v1", "policy v1", ["alice"])
        assert client.count(COLLECTION, exact=True).count == 1
        print("PASS repeated ingestion: 1 point")

        write_version(client, "team_b", "policy", "v1", "private team_b", ["bob"])
        assert retrieve(client, "team_a", "alice", {"policy"}, active) == ["policy v1"]
        assert retrieve(client, "team_a", "bob", {"policy"}, active) == []
        assert retrieve(client, "team_a", "alice", set(), active) == []
        print("PASS tenant, principal and revoked-access filters")

        write_version(client, "team_a", "policy", "v2", "policy v2", ["alice"])
        assert retrieve(client, "team_a", "alice", {"policy"}, active) == ["policy v1"]
        active[("team_a", "policy")] = "v2"
        assert retrieve(client, "team_a", "alice", {"policy"}, active) == ["policy v2"]
        print("PASS staged version invisible; switched version visible")

        del active[("team_a", "policy")]
        assert retrieve(client, "team_a", "alice", {"policy"}, active) == []
        client.delete(COLLECTION, points_selector=models.FilterSelector(
            filter=document_filter("team_a", "policy")), wait=True)
        assert client.count(COLLECTION, count_filter=document_filter("team_a", "policy"),
                            exact=True).count == 0
        assert client.count(COLLECTION, exact=True).count == 1
        print("PASS deletion: all team_a versions removed; team_b preserved")
        client.close()
        reopened = QdrantClient(path=directory)
        assert reopened.count(COLLECTION, exact=True).count == 1
        reopened.close()
        print("PASS local index survives client reopen")


if __name__ == "__main__":
    main()
