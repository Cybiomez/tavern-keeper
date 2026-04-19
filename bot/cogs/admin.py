from __future__ import annotations

from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from bot.content.texts import format_welcome
from bot.db import queries


class AdminCog(commands.Cog, name="Admin"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    set_group = app_commands.Group(
        name="set",
        description="Настройка параметров бота",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @set_group.command(name="default_role", description="Роль, выдаваемая новым участникам")
    async def set_default_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "default_role_id", role.id)
        await interaction.response.send_message(
            f"Роль новичка: **{role.name}**", ephemeral=True
        )

    @set_group.command(name="warn_role", description="Роль при достижении порога предупреждений")
    async def set_warn_role(
        self, interaction: discord.Interaction, role: discord.Role
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "warn_role_id", role.id)
        await interaction.response.send_message(
            f"Роль нарушителя: **{role.name}**", ephemeral=True
        )

    @set_group.command(name="warn_threshold", description="Кол-во предупреждений до выдачи роли нарушителя")
    async def set_warn_threshold(
        self,
        interaction: discord.Interaction,
        count: app_commands.Range[int, 1, 10],
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "warn_threshold", count)
        await interaction.response.send_message(
            f"Порог предупреждений: **{count}**", ephemeral=True
        )

    @set_group.command(name="greeting_channel", description="Канал с правилами (простынка)")
    async def set_greeting_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "greeting_channel_id", channel.id)
        await interaction.response.send_message(
            f"Канал правил: {channel.mention}", ephemeral=True
        )

    @set_group.command(name="public_channel", description="Канал для атмосферных сообщений бота")
    async def set_public_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "public_channel_id", channel.id)
        await interaction.response.send_message(
            f"Публичный канал: {channel.mention}", ephemeral=True
        )

    @set_group.command(name="mod_channel", description="Канал для команд модерации")
    async def set_mod_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "mod_channel_id", channel.id)
        await interaction.response.send_message(
            f"Канал модераторов: {channel.mention}", ephemeral=True
        )

    @set_group.command(name="log_channel", description="Канал для журнала действий бота")
    async def set_log_channel(
        self, interaction: discord.Interaction, channel: discord.TextChannel
    ) -> None:
        assert interaction.guild_id is not None
        await queries.ensure_guild_config(interaction.guild_id)
        await queries.set_guild_field(interaction.guild_id, "log_channel_id", channel.id)
        await interaction.response.send_message(
            f"Канал логов: {channel.mention}", ephemeral=True
        )

    @app_commands.command(name="post", description="Опубликовать текст от имени бота")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def post(
        self,
        interaction: discord.Interaction,
        text: Literal["rules"],
        channel: discord.TextChannel | None = None,
    ) -> None:
        target = channel or interaction.channel
        if not isinstance(target, discord.TextChannel):
            await interaction.response.send_message(
                "Укажи текстовый канал.", ephemeral=True
            )
            return
        config_obj = self.bot.config  # type: ignore[attr-defined]
        await target.send(format_welcome(config_obj.invite_url))
        await interaction.response.send_message("Опубликовано.", ephemeral=True)

    @app_commands.command(name="config", description="Показать текущие настройки бота")
    @app_commands.default_permissions(manage_guild=True)
    @app_commands.guild_only()
    async def show_config(self, interaction: discord.Interaction) -> None:
        assert interaction.guild is not None
        config = await queries.get_guild_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message(
                "Бот не настроен. Используй `/set` для начала.", ephemeral=True
            )
            return

        def fmt_role(rid: object) -> str:
            if not rid:
                return "не задана"
            role = interaction.guild.get_role(int(rid))  # type: ignore[arg-type]
            return f"**{role.name}**" if role else f"#{rid} (не найдена)"

        def fmt_ch(cid: object) -> str:
            if not cid:
                return "не задан"
            ch = interaction.guild.get_channel(int(cid))  # type: ignore[arg-type]
            return ch.mention if ch else f"#{cid} (не найден)"

        lines = [
            "**Настройки Tavern Keeper**",
            f"Роль новичка: {fmt_role(config.get('default_role_id'))}",
            f"Роль нарушителя: {fmt_role(config.get('warn_role_id'))}",
            f"Порог предупреждений: **{config.get('warn_threshold') or 2}**",
            f"Канал правил: {fmt_ch(config.get('greeting_channel_id'))}",
            f"Публичный канал: {fmt_ch(config.get('public_channel_id'))}",
            f"Канал модераторов: {fmt_ch(config.get('mod_channel_id'))}",
            f"Канал логов: {fmt_ch(config.get('log_channel_id'))}",
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
