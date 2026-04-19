from __future__ import annotations

import random
from dataclasses import dataclass

import discord
from discord.ext import commands, tasks


@dataclass
class _StatusEntry:
    text: str
    kind: discord.ActivityType


# Дополнять этот список — больше ничего трогать не нужно
STATUSES: list[_StatusEntry] = [
    _StatusEntry("Наблюдает за порядком", discord.ActivityType.watching),
    _StatusEntry("Ведёт записи", discord.ActivityType.watching),
    _StatusEntry("Считает гостей", discord.ActivityType.watching),
    _StatusEntry("Слушает разговоры", discord.ActivityType.listening),
    _StatusEntry("Полирует стойку", discord.ActivityType.playing),
    _StatusEntry("Изучает журнал посетителей", discord.ActivityType.watching),
    _StatusEntry("Готовит зал к вечеру", discord.ActivityType.playing),
]


class PresenceCog(commands.Cog, name="Presence"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._last_index: int = -1

    def cog_load(self) -> None:
        self.rotate_status.start()

    def cog_unload(self) -> None:
        self.rotate_status.cancel()

    def _pick(self) -> _StatusEntry:
        available = [i for i in range(len(STATUSES)) if i != self._last_index]
        idx = random.choice(available)
        self._last_index = idx
        return STATUSES[idx]

    @tasks.loop(hours=1)
    async def rotate_status(self) -> None:
        entry = self._pick()
        await self.bot.change_presence(
            activity=discord.Activity(type=entry.kind, name=entry.text)
        )

    @rotate_status.before_loop
    async def _before(self) -> None:
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PresenceCog(bot))
