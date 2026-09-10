"""教学模拟协议：不是 Slack API，也不向外部服务发送请求。"""

import hashlib
import hmac
import json
import random
import secrets
import sqlite3
import time


class DemoSaaS:
    """模拟一次性授权码、轮转令牌、单调 revision 和不透明游标。"""

    def __init__(self):
        self.codes = set()
        self.access = ""
        self.refresh = ""
        self.rows = [
            {"id": "n1", "revision": 1, "text": "first", "deleted": False},
            {"id": "n2", "revision": 2, "text": "second", "deleted": False},
            {"id": "n3", "revision": 3, "text": "third", "deleted": False},
        ]
        self.rate_limit_once = True
        self.cursors = {}

    def authorize(self, state):
        # 仅模拟“用户在供应商页面同意后”的回调，不模拟真实身份认证。
        code = secrets.token_urlsafe(16)
        self.codes.add(code)
        return {"code": code, "state": state}

    def token(self, grant, value):
        if grant == "authorization_code" and value in self.codes:
            self.codes.remove(value)
        elif grant == "refresh_token" and value and value == self.refresh:
            pass
        else:
            raise ValueError("reauthorization required: invalid grant")
        self.access, self.refresh = secrets.token_urlsafe(16), secrets.token_urlsafe(16)
        return {"access_token": self.access, "refresh_token": self.refresh}

    def page(self, access, after, through, cursor):
        if not access or access != self.access:
            return 401, {}, {}
        if self.rate_limit_once:
            self.rate_limit_once = False
            return 429, {"Retry-After": "2"}, {}
        rows = sorted((r for r in self.rows if after < r["revision"] <= through),
                      key=lambda r: r["revision"])
        if cursor:
            if cursor not in self.cursors:
                return 400, {}, {"error": "invalid_cursor"}
            old_after, old_through, offset = self.cursors[cursor]
            if (after, through) != (old_after, old_through):
                return 400, {}, {"error": "cursor_scope_changed"}
        else:
            offset = 0
        following = ""
        if offset + 2 < len(rows):
            following = secrets.token_urlsafe(12)
            self.cursors[following] = (after, through, offset + 2)
        return 200, {}, {"items": rows[offset:offset + 2], "next_cursor": following}


def connect(path=":memory:"):
    db = sqlite3.connect(path)
    db.executescript("""
        CREATE TABLE IF NOT EXISTS state (key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS records (
            tenant TEXT, id TEXT, revision INTEGER, text TEXT, deleted INTEGER,
            PRIMARY KEY (tenant, id));
        CREATE TABLE IF NOT EXISTS inbox (
            tenant TEXT, event_id TEXT, PRIMARY KEY (tenant, event_id));
    """)
    return db


class Integration:
    def __init__(self, provider, db, sleep=time.sleep, now=time.time):
        self.provider, self.db, self.sleep, self.now = provider, db, sleep, now
        self.tenant = "demo-team"
        self.pending = {}
        self.refresh_count = 0

    def begin_authorization(self, browser_session):
        state = secrets.token_urlsafe(24)
        self.pending[browser_session] = (state, self.now() + 300)
        return state

    def finish_authorization(self, browser_session, callback):
        expected, expires = self.pending.get(browser_session, ("", 0))
        if not expected or self.now() >= expires:
            raise ValueError("missing or expired OAuth state")
        if not hmac.compare_digest(expected, callback["state"]):
            raise ValueError("OAuth state mismatch")
        del self.pending[browser_session]
        tokens = self.provider.token("authorization_code", callback["code"])
        with self.db:
            self.save("tokens", tokens)

    def load(self, key, default):
        row = self.db.execute("SELECT value FROM state WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else default

    def save(self, key, value):
        self.db.execute("INSERT INTO state VALUES (?, ?) ON CONFLICT(key) "
                        "DO UPDATE SET value=excluded.value", (key, json.dumps(value)))

    def request_page(self, after, through, cursor):
        refreshed = False
        for attempt in range(4):
            tokens = self.load("tokens", {})
            status, headers, body = self.provider.page(
                tokens.get("access_token"), after, through, cursor)
            if status == 200:
                return body
            if status == 401 and not refreshed:
                updated = self.provider.token("refresh_token", tokens.get("refresh_token"))
                # 先保存整对轮转令牌；不与后续同步业务事务混在一起回滚。
                with self.db:
                    self.save("tokens", updated)
                self.refresh_count += 1
                refreshed = True
                continue
            if status == 429:
                value = headers.get("Retry-After")
                delay = float(value) if value is not None else min(2 ** attempt, 16) + random.random()
                self.sleep(max(0, delay))
                continue
            raise RuntimeError(f"non-retryable API status: {status}")
        raise RuntimeError("retry budget exhausted")

    def upsert(self, row):
        self.db.execute("""INSERT INTO records VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(tenant,id) DO UPDATE SET revision=excluded.revision,
            text=excluded.text, deleted=excluded.deleted
            WHERE excluded.revision > records.revision""",
            (self.tenant, row["id"], row["revision"], row["text"], int(row["deleted"])))

    def sync(self, fail_before_checkpoint=False):
        after = self.load("watermark", 0)
        through = max((r["revision"] for r in self.provider.rows), default=after)
        cursor, seen, fetched = "", set(), []
        while True:
            page = self.request_page(after, through, cursor)
            fetched.extend(page["items"])
            cursor = page["next_cursor"]
            if not cursor:
                break
            if cursor in seen:
                raise RuntimeError("cursor cycle")
            seen.add(cursor)
        # 为便于读懂，先取完本轮再一次提交；大批量同步应分批暂存。
        with self.db:
            for row in fetched:
                self.upsert(row)
            if fail_before_checkpoint:
                raise RuntimeError("injected crash before checkpoint")
            self.save("watermark", through)
        return len(fetched)


def signature(secret, timestamp, raw):
    base = b"v0:" + str(timestamp).encode() + b":" + raw
    return "v0=" + hmac.new(secret.encode(), base, hashlib.sha256).hexdigest()


def receive_webhook(app, secret, timestamp, supplied_signature, raw):
    """签名计算采用 Slack 的 v0 算法；解码后的业务 envelope 是本地教学格式。"""
    try:
        if abs(app.now() - int(timestamp)) > 300:
            return "rejected"
    except (TypeError, ValueError):
        return "rejected"
    if not hmac.compare_digest(signature(secret, timestamp, raw), supplied_signature):
        return "rejected"
    try:
        event = json.loads(raw)
        if event["tenant"] != app.tenant or not isinstance(event["event_id"], str) or not event["event_id"]:
            return "rejected"
        row = event["record"]
        if (not isinstance(row["id"], str) or not row["id"] or
                type(row["revision"]) is not int or row["revision"] < 0 or
                not isinstance(row["text"], str) or type(row["deleted"]) is not bool):
            return "rejected"
    except (ValueError, KeyError, TypeError):
        return "rejected"
    with app.db:
        inserted = app.db.execute("INSERT OR IGNORE INTO inbox VALUES (?, ?)",
                                  (event["tenant"], event["event_id"])).rowcount
        if not inserted:
            return "duplicate"
        app.upsert(row)
    return "accepted"
