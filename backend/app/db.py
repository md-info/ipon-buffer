"""SQLite demo storage; raw wallet history and AI text are never persisted."""

import hashlib
import json
import threading
import time

from sqlalchemy import Column, Integer, MetaData, String, Table, Text, create_engine, select
from sqlalchemy.pool import StaticPool

metadata = MetaData()
sessions = Table(
    "sessions",
    metadata,
    Column("id", String, primary_key=True),
    Column("state", Text, nullable=False),
)
snapshots = Table(
    "snapshots",
    metadata,
    Column("user_id", String, primary_key=True),
    Column("summary", Text, nullable=False),
)
idempotency = Table(
    "idempotency",
    metadata,
    Column("id", String, primary_key=True),
    Column("user_id", String),
    Column("fingerprint", String),
    Column("result", Text),
)
audit = Table(
    "audit",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("payload", Text),
    Column("prev_hash", String),
    Column("hash", String),
)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


class Store:
    def __init__(self, url):
        args = {"connect_args": {"check_same_thread": False}}
        if url.endswith(":memory:"):
            args["poolclass"] = StaticPool
        self.engine = create_engine(url, **args)
        metadata.create_all(self.engine)
        self.lock = threading.RLock()  # Single-process prototype; not distributed locking.
        self.drafts = {}  # Transient draft metadata, never raw prompts or provider responses.
        self.rates = {}

    def log(self, connection, user_id, action, details=None):
        prev = connection.execute(
            select(audit.c.hash).order_by(audit.c.id.desc()).limit(1)
        ).scalar()
        payload = canonical(
            {"user_id": user_id, "action": action, "ts": int(time.time()), "details": details or {}}
        )
        previous = prev or "0" * 64
        digest = hashlib.sha256((previous + payload).encode()).hexdigest()
        connection.execute(audit.insert().values(payload=payload, prev_hash=previous, hash=digest))

    def verify(self, connection):
        previous = "0" * 64
        for row in connection.execute(select(audit).order_by(audit.c.id)):
            if row.prev_hash != previous:
                return False
            if hashlib.sha256((previous + row.payload).encode()).hexdigest() != row.hash:
                return False
            previous = row.hash
        return True
