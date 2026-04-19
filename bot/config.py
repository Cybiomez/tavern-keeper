from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    token: str
    application_id: int
    invite_url: str
    dev_guild_id: int | None


def load_config() -> Config:
    return Config(
        token=os.environ["DISCORD_TOKEN"],
        application_id=int(os.environ["APPLICATION_ID"]),
        invite_url=os.environ.get("INVITE_URL", ""),
        dev_guild_id=int(v) if (v := os.environ.get("DEV_GUILD_ID")) else None,
    )
