from __future__ import annotations

import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "tavern.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS guild_config (
    guild_id             INTEGER PRIMARY KEY,
    default_role_id      INTEGER,
    warn_role_id         INTEGER,
    greeting_channel_id  INTEGER,
    public_channel_id    INTEGER,
    mod_channel_id       INTEGER,
    log_channel_id       INTEGER,
    warn_threshold       INTEGER DEFAULT 2,
    last_phrase_index    INTEGER DEFAULT -1
);

CREATE TABLE IF NOT EXISTS warnings (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    guild_id    INTEGER NOT NULL,
    user_id     INTEGER NOT NULL,
    reason      TEXT    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


async def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executescript(_SCHEMA)
        await db.commit()
