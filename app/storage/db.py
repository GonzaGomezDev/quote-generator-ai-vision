import json
from pathlib import Path

import aiosqlite

DB_PATH = Path(__file__).parent.parent.parent / "data" / "app.db"

_CREATE_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id          TEXT PRIMARY KEY,
    channel     TEXT NOT NULL,
    sender      TEXT NOT NULL,
    media_url   TEXT NOT NULL,
    received_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS extractions (
    message_id  TEXT PRIMARY KEY,
    data        TEXT NOT NULL,
    latency_ms  INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS quotes (
    message_id  TEXT PRIMARY KEY,
    sku_id      TEXT,
    sku_name    TEXT,
    quantity    INTEGER NOT NULL DEFAULT 1,
    subtotal    REAL NOT NULL DEFAULT 0,
    tax         REAL NOT NULL DEFAULT 0,
    shipping    REAL NOT NULL DEFAULT 0,
    total       REAL NOT NULL DEFAULT 0,
    currency    TEXT NOT NULL DEFAULT 'USD',
    status      TEXT NOT NULL DEFAULT 'unmatched'
);

CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    payload     TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_CREATE_SQL)
        await db.commit()


async def insert_event(payload: dict) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO events (payload) VALUES (?)",
            (json.dumps(payload),),
        )
        await db.commit()


async def fetch_recent_events(limit: int = 50) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT payload FROM events ORDER BY id DESC LIMIT ?", (limit,)
        )
        rows = await cursor.fetchall()
    return [json.loads(r["payload"]) for r in reversed(rows)]
