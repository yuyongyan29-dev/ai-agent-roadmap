"""U4.8：独立的本地压测靶场，只使用临时 SQLite 与 mock 模型。"""

import argparse
import json
import sqlite3
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def serve(port, indexed):
    with tempfile.TemporaryDirectory(prefix="roadmap-load-") as directory:
        db_path = Path(directory) / "lab.sqlite"
        with sqlite3.connect(db_path) as db:
            db.execute("CREATE TABLE items (item_key TEXT, value TEXT)")
            db.executemany("INSERT INTO items VALUES (?, ?)",
                           ((f"item-{i}", f"value-{i}") for i in range(20000)))
            if indexed:
                db.execute("CREATE INDEX item_key_idx ON items(item_key)")
            plan = db.execute("EXPLAIN QUERY PLAN SELECT value FROM items WHERE item_key = ?",
                              ("item-19999",)).fetchone()[3]
        model_slots = threading.BoundedSemaphore(2)

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                if self.path not in {"/health", "/db", "/agent"}:
                    self.send_error(404)
                    return
                result = {"mode": "local-mock", "indexed": indexed}
                status = 200
                if self.path != "/health":
                    started = time.perf_counter()
                    with sqlite3.connect(db_path) as db:
                        row = db.execute("SELECT value FROM items WHERE item_key = ?",
                                         ("item-19999",)).fetchone()
                    result.update(value=row[0], db_ms=round((time.perf_counter() - started) * 1000, 3))
                if self.path == "/agent":
                    started = time.perf_counter()
                    acquired = model_slots.acquire(timeout=0.05)
                    result["model_wait_ms"] = round((time.perf_counter() - started) * 1000, 3)
                    if acquired:
                        try:
                            started = time.perf_counter()
                            time.sleep(0.04)  # 人工设置的模型延迟，不是真实模型测量值
                            result["model_ms"] = round((time.perf_counter() - started) * 1000, 3)
                            result["answer"] = "mock answer"
                        finally:
                            model_slots.release()
                    else:
                        status = 429
                        result["error"] = "mock model concurrency limit"
                body = json.dumps(result).encode()
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

        class Server(ThreadingHTTPServer):
            request_queue_size = 128

        with Server(("127.0.0.1", port), Handler) as server:
            print(f"local-mock port={port} indexed={indexed} plan={plan}", flush=True)
            try:
                server.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--indexed", action="store_true")
    args = parser.parse_args()
    serve(args.port, args.indexed)
