#!/usr/bin/env python3

import json
import tempfile
from traceback import print_exc
import discord
from discord.ext import commands
from src.const import CHAR_LIMIT
from src.utils import get_guild_channel, get_guild_role, guild_config, has_permissions
from src.utils import try_react, try_delete


class Roles:
  @commands.command()
  @commands.guild_only()
  @commands.check(has_permissions)
  async def channel(self, ctx, *, channel: str=None):
    if not channel:
      channel = get_guild_channel(ctx.guild, guild_config(ctx.bot.db, ctx.guild.id)["channel"])

      try:
        message = (f"Current role channel: <#{channel.id}>.\n"
                   f"Use the command again to set the role channel...\n"
                   f"For example: {ctx.bot.user.mention} channel <#{ctx.channel.id}>")

      except AttributeError:
        message = (f"Use the command again to set the role channel...\n"
                   f"For example: {ctx.bot.user.mention} channel <#{ctx.channel.id}>")

      try:
        await ctx.send(message)
      except (discord.HTTPException, discord.Forbidden):
        print_exc()

      return

    try:
      channel = get_guild_channel(ctx.guild, channel)
      guild_config(ctx.bot.db, ctx.guild.id, {"channel": channel.id})
      await try_react(ctx, "✅")

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    await ctx.bot.update_roles(ctx.guild)

  @commands.command()
  @commands.guild_only()
  @commands.check(has_permissions)
  async def update(self, ctx):
    try:
      await ctx.bot.update_roles(ctx.guild)
      if ctx.channel.id == guild_config(ctx.bot.db, ctx.guild.id)["channel"]:
        await try_delete(ctx.message)

    except Exception:
      await try_react(ctx, "❗")

      print_exc()

    else:
      await try_react(ctx, "✅")

  @commands.command(aliases=["add"])
  @commands.guild_only()
  @commands.check(has_permissions)
  async def add_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [get_guild_role(ctx.guild, role) for role in roles]))
      excp = [role for role in guild_config(ctx.bot.db, ctx.guild.id).get("exceptions", []) if role not in [role.id for role in roles]]
      guild_config(ctx.bot.db, ctx.guild.id, {"exceptions": excp})

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    else:
      await try_react(ctx, "✅")

  @commands.command(aliases=["remove"])
  @commands.guild_only()
  @commands.check(has_permissions)
  async def remove_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [get_guild_role(ctx.guild, role) for role in roles]))
      excp = [role for role in guild_config(ctx.bot.db, ctx.guild.id).get("exceptions", [])] + [role.id for role in roles]
      guild_config(ctx.bot.db, ctx.guild.id, {"exceptions": list(set(excp))})

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    else:
      await try_react(ctx, "✅")

  @commands.command(aliases=["allow", "grant"])
  @commands.guild_only()
  async def allow_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [get_guild_role(ctx.guild, role) for role in roles]))
      allw = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["allowed"]] + [role.id for role in roles]
      guild_config(ctx.bot.db, ctx.guild.id, {"allowed": list(set(allw))})

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    else:
      await try_react(ctx, "✅")

  @commands.command(aliases=["unallow", "ungrant"])
  @commands.guild_only()
  async def unallow_role(self, ctx, *roles):
    try:
      assert len(roles) > 0

      roles = list(filter(lambda r: r is not None, [get_guild_role(ctx.guild, role) for role in roles]))
      allw = [role for role in guild_config(ctx.bot.db, ctx.guild.id)["allowed"] if role not in [role.id for role in roles]]
      guild_config(ctx.bot.db, ctx.guild.id, {"allowed": allw})

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    else:
      await try_react(ctx, "✅")

  @commands.command(name="roles")
  async def show_roles(self, ctx, guild_id: int=0):
    if await ctx.bot.is_owner(ctx.author):
      try:
        guild = ctx.bot.get_guild(guild_id) or ctx.guild
        assert isinstance(guild, discord.Guild)

      except Exception:
        await try_delete(ctx.message)
        print_exc()
        return

    else:
      if not (ctx.guild and has_permissions(ctx)):
        return

      guild = ctx.guild

    roles = {}
    config = guild_config(ctx.bot.db, guild.id)
    config = {"roles": config.get("roles", []), "exceptions": config.get("exceptions", [])}

    def predicate(role):
      role = get_guild_role(guild, role)

      if role:
        return [role.id, role.name]
      else:
        return None

    for key, val in config.items():
      roles[key] = list(map(predicate, val))

    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fp:
      json.dump(roles, fp, sort_keys=True, indent=2)
      fp.seek(0)

      try:
        await ctx.send(file=discord.File(fp, filename="roles.json"))
      except (discord.Forbidden, discord.HTTPException):
        print_exc()

  @commands.command(name="allowed")
  async def show_allowed_roles(self, ctx, guild_id: int=0):
    if await ctx.bot.is_owner(ctx.author):
      try:
        guild = ctx.bot.get_guild(guild_id) or ctx.guild
        assert isinstance(guild, discord.Guild)

      except Exception:
        await try_delete(ctx.message)

        print_exc()
        return

    else:
      if not (ctx.guild and has_permissions(ctx)):
        return

      guild = ctx.guild

    roles = {}
    config = guild_config(ctx.bot.db, guild.id)
    config = {"allowed": config.get("allowed")}

    def predicate(role):
      role = get_guild_role(guild, role)

      if role:
        return [role.id, role.name]
      else:
        return None

    for key, val in config.items():
      roles[key] = list(map(predicate, val))

    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fp:
      json.dump(roles, fp, sort_keys=True, indent=2)
      fp.seek(0)

      try:
        await ctx.send(file=discord.File(fp, filename="allowed.json"))
      except (discord.Forbidden, discord.HTTPException, json.JSONDecodeError):
        print_exc()


def setup(bot):
  bot.add_cog(Roles())