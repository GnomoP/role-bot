#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import traceback
import discord
from discord.ext import commands
from src.utils import fprint, guild_config
from src.const import SYNC_TIME, CHAR_LIMIT


class Owner:
  @commands.is_owner()
  @commands.command()
  async def shutdown(self, ctx):
    try:
      await ctx.message.add_reaction("👋")
    except Exception:
      pass

    await asyncio.sleep(SYNC_TIME)

    await ctx.bot.logout()
    fprint("Logged out. Shutting down...")

  @commands.is_owner()
  @commands.command()
  async def restart(self, ctx):
    try:
      await ctx.message.add_reaction("👋")
    except Exception:
      pass

    await asyncio.sleep(SYNC_TIME)

    fprint("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

  @commands.is_owner()
  @commands.command(name="config", hidden=True)
  async def get_config(self, ctx, guild_id: int=0):
    try:
      guild = ctx.bot.get_guild(guild_id) or ctx.guild
      assert isinstance(guild, discord.Guild)
    except Exception:
      try:
        await ctx.message.delete()
      except Exception:
        pass

      traceback.print_exc()
      return

    config = guild_config(ctx.bot.db, guild.id)
    message = "```json\n{}\n```".format(json.dumps(config, sort_keys=True, indent=2))[:CHAR_LIMIT]

    try:
      await ctx.send(message)
    except Exception:
      pass

  @commands.is_owner()
  @commands.command(name="load", hidden=True)
  async def load_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.load_extension("src.cogs." + cog)

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
        fprint(f"Failed to load cogs ({cog})", file=sys.stderr)
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
        fprint(f"Successfully loaded cogs ({', '.join(cogs)})")
      except Exception:
        pass

  @commands.is_owner()
  @commands.command(name="unload", hidden=True)
  async def unload_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.unload_extension("src.cogs." + cog)

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
        fprint(f"Failed to unload cogs ({cog})", file=sys.stderr)
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
        fprint(f"Successfully unloaded cogs ({', '.join(cogs)})")
      except Exception:
        pass

  @commands.is_owner()
  @commands.command(name="reload", hidden=True)
  async def reload_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.unload_extension("src.cogs." + cog)
        ctx.bot.load_extension("src.cogs." + cog)

    except Exception:
      try:
        await ctx.message.add_reaction("❗")
        fprint(f"Failed to reload cog ({cog})", file=sys.stderr)
      except Exception:
        pass

      traceback.print_exc()

    else:
      try:
        await ctx.message.add_reaction("✅")
        fprint(f"Successfully reloaded cogs ({', '.join(cogs)})")
      except Exception:
        pass


def setup(bot):
  bot.add_cog(Owner())
