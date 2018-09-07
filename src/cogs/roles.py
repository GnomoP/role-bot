#!/usr/bin/env python3

import traceback
import discord
from discord.ext import commands
from src.utils import guild_config, has_permissions


class RoleCogs:
  @commands.command()
  @commands.guild_only()
  @commands.check(has_permissions)
  async def channel(self, ctx, *, channel: str=None):
    if not channel:
      channel = self.get_guild_channel(ctx, guild_config(ctx.bot.db, ctx.guild.id)["channel"])

      try:
        message = (f"Current role channel: <#{channel.id}>.\n"
                   f"Use the command again to set the role channel...\n"
                   f"For example: {ctx.bot.user.mention} channel <#{ctx.channel.id}>")

      except AttributeError:
        message = (f"Use the command again to set the role channel...\n"
                   f"For example: {ctx.bot.user.mention} channel <#{ctx.channel.id}>")

      try:
        await ctx.send(message)
      except Exception:
        traceback.print_exc()

      return

    try:
      channel = self.get_guild_channel(ctx, channel)
      guild_config(ctx.bot.db, ctx.guild.id, {"channel": channel.id})
      await ctx.message.add_reaction("✅")

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    await ctx.bot.update_roles(ctx.guild)

  @commands.command()
  @commands.guild_only()
  @commands.check(has_permissions)
  async def update(self, ctx):
    try:
      await ctx.bot.update_roles(ctx.guild)
      if ctx.channel.id == guild_config(ctx.bot.db, ctx.guild.id)["channel"]:
        try:
          await ctx.message.delete()
        except Exception:
          pass

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
      except Exception:
        pass

  @commands.command(aliases=["add"])
  @commands.guild_only()
  @commands.check(has_permissions)
  async def add_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [self.get_guild_role(ctx, role) for role in roles]))
      excp = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["exceptions"] if role not in [role.id for role in roles]]
      guild_config(ctx.bot.db, ctx.guild.id, {"exceptions": excp})

      await ctx.bot.update_roles(ctx.guild)

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
      except Exception:
        pass

  @commands.command(aliases=["remove"])
  @commands.guild_only()
  @commands.check(has_permissions)
  async def remove_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [self.get_guild_role(ctx, role) for role in roles]))
      excp = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["exceptions"]] + [role.id for role in roles]
      guild_config(ctx.bot.db, ctx.guild.id, {"exceptions": list(set(excp))})

      await ctx.bot.update_roles(ctx.guild)

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
      except Exception:
        pass

  @commands.command(aliases=["allow", "grant"])
  @commands.guild_only()
  async def allow_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [self.get_guild_role(ctx, role) for role in roles]))
      allw = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["allowed"]] + [role.id for role in roles]
      guild_config(ctx.bot.db, ctx.guild.id, {"allowed": list(set(allw))})

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
      except Exception:
        pass

  @commands.command(aliases=["unallow", "ungrant"])
  @commands.guild_only()
  async def unallow_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [self.get_guild_role(ctx, role) for role in roles]))
      allw = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["allowed"] if role not in [role.id for role in roles]]
      guild_config(ctx.bot.db, ctx.guild.id, {"allowed": allw})

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
      except Exception:
        pass

  def get_guild_channel(self, ctx, id):
    if isinstance(id, int):
      channel = ctx.guild.get_channel(id)

      if isinstance(channel, discord.TextChannel):
        return channel
      else:
        return None

    elif isinstance(id, str):
      try:
        channel = ctx.guild.get_channel(int(id))

      except Exception:
        pass

      else:
        if isinstance(channel, discord.TextChannel):
          return channel
        else:
          return None

      try:
        channel = ctx.guild.get_channel(int(id[2:-1]))

      except Exception:
        pass

      else:
        if isinstance(channel, discord.TextChannel):
          return channel
        else:
          return None

    else:
      return None

  def get_guild_role(self, ctx, id):
    for role in ctx.guild.roles:
      if isinstance(id, int) and role.id == id:
        break

      if isinstance(id, str):
        if role.name == id:
          break

        try:
          if role.id == int(id):
            break
          if role.id == int(id[3:-1]):
            break

        except Exception:
          pass

    else:
      return None

    return role


def setup(bot):
  bot.add_cog(RoleCogs())