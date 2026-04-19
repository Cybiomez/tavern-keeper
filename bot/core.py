from __future__ import annotations

import discord
from discord.ext import commands

from bot.config import Config
from bot.db import queries

_COGS: list[str] = [
    "bot.cogs.greetings",
    "bot.cogs.roles",
    "bot.cogs.moderation",
    "bot.cogs.admin",
    "bot.cogs.presence",
    "bot.cogs.voice",
]


class TavernKeeper(commands.Bot):
    def __init__(self, config: Config) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.voice_states = True
        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=intents,
            application_id=config.application_id,
        )
        self.config: Config = config

    async def setup_hook(self) -> None:
        for cog in _COGS:
            await self.load_extension(cog)

        if self.config.dev_guild_id:
            guild = discord.Object(id=self.config.dev_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"[Tavern Keeper] Commands synced to dev guild {self.config.dev_guild_id}.")
        else:
            await self.tree.sync()
            print("[Tavern Keeper] Commands synced globally.")

    async def on_ready(self) -> None:
        assert self.user is not None
        print(f"[Tavern Keeper] Ready. {self.user} ({self.user.id})")

    async def send_log(self, guild: discord.Guild, message: str) -> None:
        config = await queries.get_guild_config(guild.id)
        if not config or not config.get("log_channel_id"):
            return
        channel = guild.get_channel(int(config["log_channel_id"]))
        if isinstance(channel, discord.TextChannel):
            await channel.send(message)
