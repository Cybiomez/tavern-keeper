from __future__ import annotations

import random

import discord
from discord.ext import commands

from bot.db import queries

# Кто-то заходит в пустой канал
_JOIN_ALONE: list[str] = [
    "Кто-то занял одинокий столик. В зале стало чуть теплее.",
    "Один из столиков перестал пустовать.",
    "Кто-то устроился в уголке. Тихо, но уже не совсем.",
]

# Кто-то заходит в непустой канал
_JOIN_CROWD: list[str] = [
    "За одним из столиков прибавилось народу.",
    "Кто-то подсел поближе к разговору.",
    "В таверне стало чуть оживлённее.",
]

# Кто-то уходит, в канале остались люди
_LEAVE: list[str] = [
    "Кто-то поднялся и вышел, не прощаясь.",
    "За одним из столиков стало тише.",
    "Чья-то кружка остыла на столе.",
]

# Последний ушёл — канал опустел
_LEAVE_EMPTY: list[str] = [
    "Столик опустел.",
    "Последний гость покинул своё место.",
    "Тишина снова заняла своё место за столом.",
]

# Кто-то перешёл в AFK-канал
_AFK: list[str] = [
    "Кто-то задремал у камина.",
    "Одним бодрствующим в зале стало меньше.",
    "В дальнем углу кто-то нашёл себе тихое место.",
]


class VoiceCog(commands.Cog, name="Voice"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        if member.bot:
            return
        if before.channel == after.channel:
            return

        guild = member.guild
        config = await queries.get_guild_config(guild.id)
        if not config or not config.get("public_channel_id"):
            return

        pub = guild.get_channel(int(config["public_channel_id"]))
        if not isinstance(pub, discord.TextChannel):
            return

        phrase = self._pick_phrase(guild, member, before.channel, after.channel)
        if phrase:
            await pub.send(phrase)

    @staticmethod
    def _pick_phrase(
        guild: discord.Guild,
        member: discord.Member,
        before: discord.VoiceChannel | discord.StageChannel | None,
        after: discord.VoiceChannel | discord.StageChannel | None,
    ) -> str | None:
        afk_id = guild.afk_channel.id if guild.afk_channel else None

        if after is not None:
            # Зашёл (из ниоткуда или переместился)
            if afk_id and after.id == afk_id:
                return random.choice(_AFK)
            others = [m for m in after.members if not m.bot and m.id != member.id]
            return random.choice(_JOIN_CROWD if others else _JOIN_ALONE)

        if before is not None:
            # Ушёл (и никуда не переместился)
            remaining = [m for m in before.members if not m.bot]
            return random.choice(_LEAVE_EMPTY if not remaining else _LEAVE)

        return None


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(VoiceCog(bot))
