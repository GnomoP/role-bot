#!/usr/bin/env python3

import discord
from discord.ext import commands
from src.utils import fprint, guild_config


class Events:
  def __init__(self, bot):
    self.bot = bot
    self.db = bot.db

  async def on_command_completion(self, ctx):
    author = ctx.message.author

    if await ctx.bot.is_owner(author):
      return

    command = ctx.command
    content = ctx.message.content

    content.replace(ctx.me.mention, f"@{ctx.me.name}")
    if len(content) > 100:
      content = content[:100] + " [...]"

    fprint(f"{author.name}#{author.discriminator} invoked '{command.name}' command: {content}")

  async def on_guild_join(self, guild):
    fprint(f"Joined a new guild: '{guild.name}' ({guild.id})")
    guild_config(self.db, guild.id)

  async def on_guild_remove(self, guild):
    fprint(f"Left a guild: '{guild.name}' ({guild.id})")
    self.db.delete(guild.id)


def setup(bot):
  bot.add_cog(Events(bot))
