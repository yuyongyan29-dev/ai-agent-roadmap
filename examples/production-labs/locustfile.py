"""一次只压一个层次；429 也算失败，避免隐藏容量边界。"""

import os
from urllib.parse import urlparse

from locust import HttpUser, constant, task


class LabUser(HttpUser):
    wait_time = constant(0.02)

    def on_start(self):
        target = urlparse(self.host)
        if target.scheme != "http" or target.hostname != "127.0.0.1":
            raise ValueError("This lab only accepts http://127.0.0.1")
        self.path = os.getenv("LAB_PATH", "/health")
        if self.path not in {"/health", "/db", "/agent"}:
            raise ValueError("LAB_PATH must be /health, /db or /agent")

    @task
    def probe(self):
        with self.client.get(self.path, timeout=2, catch_response=True) as response:
            if response.status_code == 200 and response.json().get("mode") != "local-mock":
                response.failure("Not the local mock lab")
