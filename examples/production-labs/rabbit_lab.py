"""U4.3：一次消费一条，复现提交后、ack 前崩溃；不是生产 worker。"""

import argparse
import json
import os
import sqlite3
import time

import pika

QUEUE = "roadmap.lab.tasks"
DEAD = "roadmap.lab.dead"


def publish(channel, task):
    channel.basic_publish(
        exchange="", routing_key=QUEUE, body=json.dumps(task), mandatory=True,
        properties=pika.BasicProperties(delivery_mode=2, content_type="application/json",
                                        message_id=task["id"]),
    )
    print(f"confirmed task={task['id']} attempt={task['attempt']}", flush=True)


def effect_once(db_path, task_id):
    # 唯一键和这次模拟的业务写入是同一笔事务，不用先查再写。
    with sqlite3.connect(db_path) as db:
        db.execute("CREATE TABLE IF NOT EXISTS effects (task_id TEXT PRIMARY KEY, result TEXT)")
        cursor = db.execute("INSERT OR IGNORE INTO effects VALUES (?, ?)", (task_id, "done"))
        return cursor.rowcount == 1


def main(args):
    connection = pika.BlockingConnection(pika.ConnectionParameters("127.0.0.1"))
    channel = connection.channel()
    channel.exchange_declare("roadmap.lab.dlx", exchange_type="direct", durable=True)
    channel.queue_declare(DEAD, durable=True)
    channel.queue_bind(DEAD, "roadmap.lab.dlx", routing_key="failed")
    channel.queue_declare(QUEUE, durable=True, arguments={
        "x-dead-letter-exchange": "roadmap.lab.dlx",
        "x-dead-letter-routing-key": "failed",
    })
    channel.confirm_delivery()
    try:
        if args.command == "publish":
            publish(channel, {"id": args.id, "fail": args.fail, "attempt": 0,
                              "created_at": time.time()})
        elif args.command == "status":
            for name in (QUEUE, DEAD):
                result = channel.queue_declare(name, passive=True)
                print(f"{name} ready={result.method.message_count}")
            with sqlite3.connect(args.db) as db:
                exists = db.execute("SELECT name FROM sqlite_master WHERE name='effects'").fetchone()
                print("effects=", db.execute("SELECT * FROM effects ORDER BY task_id").fetchall() if exists else [])
        elif args.command == "work":
            # basic_get 是单步演练。生产 basic_consume 应另配 prefetch_count；prefetch 不约束 basic_get。
            method, properties, body = channel.basic_get(QUEUE, auto_ack=False)
            if method is None:
                print("empty")
                return
            task = json.loads(body)
            print(f"received task={task['id']} redelivered={method.redelivered} "
                  f"queue_age_s={time.time() - task['created_at']:.3f}", flush=True)
            if task["fail"]:
                if task["attempt"] < 2:
                    task["attempt"] += 1
                    # confirm 成功后再 ack 旧消息；中途崩溃仍可能重复，所以 id 保持不变。
                    publish(channel, task)
                    channel.basic_ack(method.delivery_tag)
                    print("retry published; original acked")
                else:
                    channel.basic_nack(method.delivery_tag, requeue=False)
                    print("rejected to dead-letter exchange")
                return
            inserted = effect_once(args.db, task["id"])
            print(f"effect_inserted={inserted}", flush=True)
            if args.crash_after_commit:
                print("crash after DB commit, before ack", flush=True)
                os._exit(9)
            channel.basic_ack(method.delivery_tag)
            print("acked")
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["publish", "work", "status"])
    parser.add_argument("--id", default="task-1")
    parser.add_argument("--fail", action="store_true")
    parser.add_argument("--db", default="rabbit-lab.sqlite")
    parser.add_argument("--crash-after-commit", action="store_true")
    main(parser.parse_args())
