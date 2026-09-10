"""可复现故障注入，不登录 SaaS；假时钟和假 sleep 使验证无需等待。"""

import json
import tempfile
from pathlib import Path

from lab import DemoSaaS, Integration, connect, receive_webhook, signature


def must_fail(action, expected):
    try:
        action()
    except (ValueError, RuntimeError) as exc:
        assert expected in str(exc), str(exc)
    else:
        raise AssertionError("expected failure")


def main():
    with tempfile.TemporaryDirectory(prefix="saas-lab-") as directory:
        path = Path(directory) / "state.sqlite"
        provider, delays = DemoSaaS(), []
        app = Integration(provider, connect(path), sleep=delays.append, now=lambda: 1000)
        state = app.begin_authorization("browser-1")
        callback = provider.authorize(state)
        must_fail(lambda: app.finish_authorization("browser-2", callback), "state")
        must_fail(lambda: app.finish_authorization("browser-1", dict(callback, state="forged")), "mismatch")
        app.finish_authorization("browser-1", callback)
        must_fail(lambda: app.finish_authorization("browser-1", callback), "state")
        must_fail(lambda: provider.token("authorization_code", callback["code"]), "invalid grant")
        expired = provider.authorize(app.begin_authorization("browser-3"))
        app.now = lambda: 1400
        must_fail(lambda: app.finish_authorization("browser-3", expired), "expired")
        app.now = lambda: 1000
        print("PASS OAuth state binding, expiry and callback replay")

        old_refresh = app.load("tokens", {})["refresh_token"]
        provider.access = "expired-for-test"
        assert app.sync() == 3
        assert app.refresh_count == 1 and delays == [2.0]
        must_fail(lambda: provider.token("refresh_token", old_refresh), "invalid grant")
        assert app.load("watermark", 0) == 3
        print("PASS token rotation, opaque pagination and Retry-After=2")

        provider.rows[0] = dict(provider.rows[0], revision=4, text="updated")
        provider.rows[2] = dict(provider.rows[2], revision=5, deleted=True)
        must_fail(lambda: app.sync(fail_before_checkpoint=True), "injected crash")
        assert app.load("watermark", 0) == 3
        assert app.db.execute("SELECT text FROM records WHERE id='n1'").fetchone()[0] == "first"
        app.db.close()
        app = Integration(provider, connect(path), sleep=delays.append, now=lambda: 1000)
        assert app.sync() == 2 and app.sync() == 0
        assert app.load("watermark", 0) == 5
        assert app.db.execute("SELECT count(*) FROM records WHERE deleted=0").fetchone()[0] == 2
        print("PASS restart, transaction rollback, incremental update and tombstone")

        event = {"tenant": "demo-team", "event_id": "ev-1", "record":
                 {"id": "n1", "revision": 6, "text": "webhook update", "deleted": False}}
        raw = json.dumps(event, separators=(",", ":")).encode()
        secret, timestamp = "local-demo-secret", 1000
        signed = signature(secret, timestamp, raw)
        assert receive_webhook(app, secret, timestamp, signed, raw + b" ") == "rejected"
        assert receive_webhook(app, secret, 699, signature(secret, 699, raw), raw) == "rejected"
        assert receive_webhook(app, secret, timestamp, signed, raw) == "accepted"
        app.db.close()
        app = Integration(provider, connect(path), sleep=delays.append, now=lambda: 1000)
        assert receive_webhook(app, secret, timestamp, signed, raw) == "duplicate"
        event["event_id"] = "ev-older"
        event["record"].update(revision=2, text="old")
        older = json.dumps(event).encode()
        assert receive_webhook(app, secret, timestamp, signature(secret, timestamp, older), older) == "accepted"
        assert app.db.execute("SELECT text FROM records WHERE id='n1'").fetchone()[0] == "webhook update"
        assert app.load("watermark", 0) == 5
        print("PASS raw-body signature, replay window, persistent dedup and stale event")

        event["event_id"] = "ev-rollback"
        event["record"].update(revision=7, text="after retry")
        rollback_raw = json.dumps(event).encode()
        rollback_sig = signature(secret, timestamp, rollback_raw)
        original_upsert = app.upsert
        def fail_upsert(row):
            raise RuntimeError("injected webhook failure")
        app.upsert = fail_upsert
        must_fail(lambda: receive_webhook(app, secret, timestamp, rollback_sig, rollback_raw),
                  "injected webhook failure")
        app.upsert = original_upsert
        assert receive_webhook(app, secret, timestamp, rollback_sig, rollback_raw) == "accepted"
        assert app.db.execute("SELECT text FROM records WHERE id='n1'").fetchone()[0] == "after retry"
        print("PASS webhook inbox and record rollback together")

        provider.page = lambda *args: (429, {}, {})
        must_fail(lambda: app.request_page(0, 5, ""), "retry budget exhausted")
        assert len(delays) == 5
        print("PASS bounded retry without Retry-After")
        app.db.close()


if __name__ == "__main__":
    main()
