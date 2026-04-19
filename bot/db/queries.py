from __future__ import annotations

from typing import Any

import aiosqlite

from bot.db.database import DB_PATH

_VALID_FIELDS = frozenset(
    {
        "default_role_id",
        "warn_role_id",
        "greeting_channel_id",
        "public_channel_id",
        "mod_channel_id",
        "log_channel_id",
        "warn_threshold",
        "last_phrase_index",
    }
)


async def get_guild_config(guild_id: int) -> dict[str, Any] | None:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM guild_config WHERE guild_id = ?", (guild_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None


async def ensure_guild_config(guild_id: int) -> None:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO guild_config (guild_id) VALUES (?)", (guild_id,)
        )
        await db.commit()


async def set_guild_field(guild_id: int, field: str, value: int) -> None:
    if field not in _VALID_FIELDS:
        raise ValueError(f"Unknown config field: {field}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            f"UPDATE guild_config SET {field} = ? WHERE guild_id = ?",
            (value, guild_id),
        )
        await db.commit()


async def add_warning(guild_id: int, user_id: int, reason: str) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO warnings (guild_id, user_id, reason) VALUES (?, ?, ?)",
            (guild_id, user_id, reason),
        )
        await db.commit()
        async with db.execute(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 1


async def get_warnings(guild_id: int, user_id: int) -> list[dict[str, Any]]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT reason, created_at FROM warnings "
            "WHERE guild_id = ? AND user_id = ? ORDER BY created_at",
            (guild_id, user_id),
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]


async def remove_last_warning(guild_id: int, user_id: int) -> int:
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            """DELETE FROM warnings WHERE id = (
                SELECT id FROM warnings
                WHERE guild_id = ? AND user_id = ?
                ORDER BY created_at DESC LIMIT 1
            )""",
            (guild_id, user_id),
        )
        await db.commit()
        async with db.execute(
            "SELECT COUNT(*) FROM warnings WHERE guild_id = ? AND user_id = ?",
            (guild_id, user_id),
        ) as cursor:
            row = await cursor.fetchone()
            return int(row[0]) if row else 0
