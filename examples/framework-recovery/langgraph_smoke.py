# /// script
# requires-python = ">=3.11"
# dependencies = ["langgraph==1.2.11", "langgraph-checkpoint-sqlite==3.1.1"]
# ///
"""无模型调用：跨进程人工确认、拒绝、写入后崩溃和幂等恢复。"""
import os
from pathlib import Path
import sqlite3
import subprocess
import sys
from tempfile import TemporaryDirectory
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command, interrupt


class State(TypedDict):
    job_id: str
    approved: bool
    status: str


def worker(directory, job_id, action, crash):
    ledger_path = Path(directory) / "ledger.sqlite"
    with sqlite3.connect(ledger_path) as ledger:
        ledger.execute("CREATE TABLE IF NOT EXISTS effects (job_id TEXT PRIMARY KEY)")

    def review(state):
        decision = interrupt({"job_id": state["job_id"], "action": "write_demo_receipt"})
        # 演示只接受显式 bool True；HTTP 版必须先校验审批者和请求版本。
        return {"approved": decision is True}

    def execute(state):
        if not state["approved"]:
            return {"status": "rejected"}
        with sqlite3.connect(ledger_path) as ledger:
            ledger.execute("INSERT OR IGNORE INTO effects VALUES (?)", (state["job_id"],))
        if crash:
            # 故意在业务提交后、图 checkpoint 前中断进程。
            os._exit(70)
        return {"status": "done"}

    graph = StateGraph(State)
    graph.add_node("review", review)
    graph.add_node("execute", execute)
    graph.add_edge(START, "review")
    graph.add_edge("review", "execute")
    graph.add_edge("execute", END)
    config = {"configurable": {"thread_id": job_id}}
    with SqliteSaver.from_conn_string(str(Path(directory) / "checkpoints.sqlite")) as saver:
        app = graph.compile(checkpointer=saver)
        if action == "start":
            result = app.invoke({"job_id": job_id, "approved": False, "status": "new"}, config)
            assert result["__interrupt__"]
            print("paused")
        else:
            data = Command(resume=action == "approve") if action != "resume" else None
            result = app.invoke(data, config)
            print(result["status"])


def main():
    with TemporaryDirectory(prefix="framework-recovery-") as directory:
        def run(job, action, crash=False):
            command = [sys.executable, str(Path(__file__).resolve()), "worker",
                       directory, job, action, "crash" if crash else "normal"]
            result = subprocess.run(command, capture_output=True, text=True, timeout=30)
            assert result.returncode == (70 if crash else 0), result.stderr
            return result.stdout.strip()

        def count(job):
            with sqlite3.connect(Path(directory) / "ledger.sqlite") as ledger:
                return ledger.execute("SELECT count(*) FROM effects WHERE job_id = ?", (job,)).fetchone()[0]

        assert run("approved", "start") == "paused"
        assert count("approved") == 0
        assert run("approved", "approve") == "done"
        assert count("approved") == 1
        print("PASS pause in process A; approve in process B; effects=1")
        assert run("denied", "start") == "paused"
        assert run("denied", "reject") == "rejected"
        assert count("denied") == 0
        print("PASS reject after restart; effects=0")
        assert run("crashed", "start") == "paused"
        run("crashed", "approve", crash=True)
        assert count("crashed") == 1
        assert run("crashed", "resume") == "done"
        assert run("crashed", "resume") == "done"
        assert count("crashed") == 1
        print("PASS exit after business commit; resume twice; effects=1")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        worker(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5] == "crash")
    else:
        main()
