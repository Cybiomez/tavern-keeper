from __future__ import annotations

import discord
from discord.ext import commands

from bot.db import queries
from bot.content.phrases import pick_phrase


class GreetingsCog(commands.Cog, name="Greetings"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        guild = member.guild
        config = await queries.get_guild_config(guild.id)
        if not config:
            return

        if config.get("default_role_id"):
            role = guild.get_role(int(config["default_role_id"]))
            if role:
                try:
                    await member.add_roles(role, reason="Автоматическая роль при входе")
                except discord.Forbidden:
                    pass

        ch_id = config.get("guests_channel_id") or config.get("public_channel_id")
        if ch_id:
            channel = guild.get_channel(int(ch_id))
            if isinstance(channel, discord.TextChannel):
                last_index = int(config.get("last_phrase_index") or -1)
                phrase, new_index = pick_phrase(last_index)
                await channel.send(phrase)
                await queries.set_guild_field(guild.id, "last_phrase_index", new_index)

        await self.bot.send_log(  # type: ignore[attr-defined]
            guild,
            f"📥 **{member}** (`{member.id}`) присоединился к серверу.",
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GreetingsCog(bot))
