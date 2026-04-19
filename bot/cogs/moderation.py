from __future__ import annotations

import random

import discord
from discord import app_commands
from discord.ext import commands

from bot.db import queries

_WARN_PHRASES = [
    "Смотритель откладывает перо. Взгляд медленно останавливается на {mention}.\n— {reason}",
    "Смотритель поднимает голову. В зале на миг становится тише.\n{mention} — {reason}",
    "Перо скрипит и замирает. Смотритель смотрит на {mention} долго, не отрывая взгляда.\n— {reason}",
]

_WARN_REPEAT_PHRASES = [
    "Смотритель встаёт из-за стойки. Медленно подходит к {mention}. Молча смотрит.\n— {reason}\n*Предупреждение {count}.*",
    "В зале тихо. Смотритель кладёт перо и поднимается. {mention} — снова.\n— {reason}\n*{count}-е предупреждение.*",
    "Смотритель закрывает книгу. Встаёт. Один короткий взгляд на {mention} — и в зале всё понимают.\n— {reason}\n*Предупреждение {count}.*",
]

_KICK_PHRASES = [
    "Смотритель поднимается и молча указывает {mention} на выход. Тот уходит.\n*Причина: {reason}*",
    "В зале тихо. Смотритель кивает {mention} на дверь. Спорить не принято.\n*Причина: {reason}*",
    "Смотритель закрывает книгу. Встаёт. Один взгляд — и {mention} понимает всё.\n*Причина: {reason}*",
]


def _pick_warn(count: int, mention: str, reason: str) -> str:
    pool = _WARN_REPEAT_PHRASES if count >= 2 else _WARN_PHRASES
    return random.choice(pool).format(mention=mention, reason=reason, count=count)


class ModerationCog(commands.Cog, name="Moderation"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="warn", description="Вынести предупреждение участнику")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
    ) -> None:
        assert interaction.guild is not None
        config = await queries.get_guild_config(interaction.guild.id)
        count = await queries.add_warning(interaction.guild.id, member.id, reason)
        threshold = int(config.get("warn_threshold") or 2) if config else 2

        phrase = _pick_warn(count, member.mention, reason)

        if config and config.get("public_channel_id"):
            ch = interaction.guild.get_channel(int(config["public_channel_id"]))
            if isinstance(ch, discord.TextChannel):
                await ch.send(phrase)

        if count >= threshold and config and config.get("warn_role_id"):
            warn_role = interaction.guild.get_role(int(config["warn_role_id"]))
            if warn_role and warn_role not in member.roles:
                await member.add_roles(
                    warn_role, reason=f"Порог предупреждений достигнут ({threshold})"
                )

        await self.bot.send_log(  # type: ignore[attr-defined]
            interaction.guild,
            f"⚠️ **{interaction.user}** предупредил {member.mention} (#{count}): {reason}",
        )
        await interaction.response.send_message(
            f"Предупреждение #{count} вынесено.", ephemeral=True
        )

    @app_commands.command(name="warnings", description="Показать предупреждения участника")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        assert interaction.guild is not None
        warns = await queries.get_warnings(interaction.guild.id, member.id)
        if not warns:
            await interaction.response.send_message(
                f"У {member.mention} нет предупреждений.", ephemeral=True
            )
            return
        lines = [f"**Предупреждения {member.mention}** ({len(warns)}):"]
        for i, w in enumerate(warns, 1):
            date = str(w["created_at"])[:10]
            lines.append(f"`{i}.` {w['reason']} — {date}")
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @app_commands.command(name="unwarn", description="Снять последнее предупреждение")
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.guild_only()
    async def unwarn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
    ) -> None:
        assert interaction.guild is not None
        remaining = await queries.remove_last_warning(interaction.guild.id, member.id)
        await self.bot.send_log(  # type: ignore[attr-defined]
            interaction.guild,
            f"↩️ **{interaction.user}** снял предупреждение с {member.mention}. Осталось: {remaining}",
        )
        await interaction.response.send_message(
            f"Последнее предупреждение снято. Осталось: **{remaining}**.", ephemeral=True
        )

    @app_commands.command(name="kick", description="Выгнать участника из таверны")
    @app_commands.default_permissions(kick_members=True)
    @app_commands.guild_only()
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str,
    ) -> None:
        assert interaction.guild is not None
        config = await queries.get_guild_config(interaction.guild.id)

        phrase = random.choice(_KICK_PHRASES).format(
            mention=member.mention, reason=reason
        )

        if config and config.get("public_channel_id"):
            ch = interaction.guild.get_channel(int(config["public_channel_id"]))
            if isinstance(ch, discord.TextChannel):
                await ch.send(phrase)

        await self.bot.send_log(  # type: ignore[attr-defined]
            interaction.guild,
            f"🚪 **{interaction.user}** выгнал {member.mention}: {reason}",
        )
        await member.kick(reason=reason)
        await interaction.response.send_message("Участник выгнан.", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModerationCog(bot))
