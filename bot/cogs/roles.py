from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class RolesCog(commands.Cog, name="Roles"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    role_group = app_commands.Group(
        name="role",
        description="Управление ролями участников",
        default_permissions=discord.Permissions(manage_roles=True),
    )

    @role_group.command(name="give", description="Выдать роль участнику")
    async def role_give(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        await member.add_roles(
            role, reason=f"Выдано через /role give — {interaction.user}"
        )
        await self.bot.send_log(  # type: ignore[attr-defined]
            interaction.guild,  # type: ignore[arg-type]
            f"🎭 **{interaction.user}** выдал роль **{role.name}** → {member.mention}",
        )
        await interaction.response.send_message(
            f"Роль **{role.name}** выдана {member.mention}.", ephemeral=True
        )

    @role_group.command(name="take", description="Забрать роль у участника")
    async def role_take(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
    ) -> None:
        await member.remove_roles(
            role, reason=f"Забрано через /role take — {interaction.user}"
        )
        await self.bot.send_log(  # type: ignore[attr-defined]
            interaction.guild,  # type: ignore[arg-type]
            f"🎭 **{interaction.user}** забрал роль **{role.name}** у {member.mention}",
        )
        await interaction.response.send_message(
            f"Роль **{role.name}** забрана у {member.mention}.", ephemeral=True
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RolesCog(bot))
