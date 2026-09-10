"""U3.5：用真实 Langfuse SDK 验证父子 span，导出到内存，不连接平台。"""

from langfuse import Langfuse
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter


def main():
    exporter = InMemorySpanExporter()
    lf = Langfuse(public_key="pk-lab", secret_key="sk-lab", base_url="http://127.0.0.1:9",
                  span_exporter=exporter)
    with lf.start_as_current_observation(as_type="span", name="agent-run", input="查询保修条款",
                                         metadata={"prompt_version": "lab-v1", "code_version": "local"}) as root:
        with lf.start_as_current_observation(as_type="span", name="turn-1"):
            with lf.start_as_current_observation(as_type="generation", name="llm-call", model="mock") as gen:
                gen.update(input=[{"role": "user", "content": "查询保修条款"}],
                           output={"tool": "search_docs"}, metadata={"finish_reason": "tool_calls", "mock": True})
            with lf.start_as_current_observation(as_type="span", name="tool:search_docs") as tool:
                tool.update(input={"query": "保修"}, output={"doc_id": "policy-v1", "text": "保修期 12 个月"},
                            metadata={"truncated": False, "corpus_version": "lab-v1"})
        root.update(output="保修期 12 个月")
    lf.flush()
    spans = {span.name: span for span in exporter.get_finished_spans()}
    assert set(spans) == {"agent-run", "turn-1", "llm-call", "tool:search_docs"}
    assert spans["turn-1"].parent.span_id == spans["agent-run"].context.span_id
    for name in ("llm-call", "tool:search_docs"):
        assert spans[name].parent.span_id == spans["turn-1"].context.span_id
    assert len({span.context.trace_id for span in spans.values()}) == 1
    print("spans=4 one_trace=True parent_links=True")
    print("export=in-memory model=mock remote_ingestion=not-tested")
    lf.shutdown()


if __name__ == "__main__":
    main()
