#!/usr/bin/env python3

import os
import sys
import asyncio
import traceback
from discord.ext import commands
from src.utils import fprint
from src.const import SYNC_TIME


class OwnerCogs:
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
  bot.add_cog(OwnerCogs())
