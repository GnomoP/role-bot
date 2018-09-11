#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import tempfile
from traceback import print_exc
import discord
from discord.ext import commands
from src.const import SYNC_TIME, CHAR_LIMIT
from src.utils import fprint, guild_config
from src.utils import try_react, try_delete


class Owner:
  @commands.is_owner()
  @commands.command()
  async def shutdown(self, ctx):
    await try_react(ctx, "👋")
    await asyncio.sleep(SYNC_TIME)

    await ctx.bot.logout()
    fprint("Logged out. Shutting down...")

  @commands.is_owner()
  @commands.command()
  async def restart(self, ctx):
    await try_react(ctx, "👋")
    await asyncio.sleep(SYNC_TIME)

    fprint("Restarting...")
    os.execl(sys.executable, sys.executable, *sys.argv)

  @commands.is_owner()
  @commands.command()
  async def purge(self, ctx, limit: int=200):
    def predicate(m):
      return m.id != ctx.message.id and (m.author.id == ctx.me.id or ctx.me in m.mentions)

    try:
      await ctx.channel.purge(limit=limit, check=predicate)

    except Exception:
      fprint(f"Failed to delete message in channel #{ctx.channel.name} ({ctx.channel.id})", file=sys.stderr)
      await try_react(ctx, "❗")

    else:
      await try_react(ctx, "✅")

  @commands.is_owner()
  @commands.command(name="exec", aliases=["python", "py"], hidden=True)
  async def pyexec(self, ctx, *, code):
    try:
      g = {
        "cog": self,
        "json": json,
        "ctx": ctx,
        "bot": ctx.bot,
        "db": ctx.bot.db,
      }

      cc = compile(code, "vot_exec.py", "exec")
      exec(cc, g)
    except (discord.HTTPException, discord.Forbidden):
      pass
    except Exception:
      await try_react(ctx, "❗")

      print_exc()
    else:
      await try_react(ctx, "✅")

  @commands.is_owner()
  @commands.command(name="eval")
  async def pyeval(self, ctx, *, code):
    val = ""

    try:
      g = {
        "cog": self,
        "json": json,
        "ctx": ctx,
        "bot": ctx.bot,
        "db": ctx.bot.db,
      }

      cc = compile(code, "bot_eval.py", "eval")
      val = str(eval(cc, g))

    except (discord.HTTPException, discord.Forbidden):
      pass

    except (SyntaxError, ValueError):
      await try_react(ctx, "❓")
      print_exc()

    except Exception:
      await try_react(ctx, "❗")
      print_exc()

    else:
      await try_react(ctx, "✅")

    if len(val) == 0:
      return

    elif len(val) + 2 < 50:
      await ctx.send(f"`{val}`")

    elif len(val) + 8 < CHAR_LIMIT:
      await ctx.send(f"```\n{val}\n```")

    else:
      with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fp:
        fp.write(val)
        fp.seek(0)

        try:
          await ctx.send(file=discord.File(fp, filename="output.txt"))
        except (discord.Forbidden, discord.HTTPException):
          print_exc()

  @commands.is_owner()
  @commands.command(name="config", hidden=True)
  async def get_config(self, ctx, guild_id: int=0):
    try:
      guild = ctx.bot.get_guild(guild_id) or ctx.guild
      assert isinstance(guild, discord.Guild)

    except Exception:
      await try_delete(ctx.message)
      print_exc()
      return

    config = guild_config(ctx.bot.db, guild.id)
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fp:
      json.dump(config, fp, sort_keys=True, indent=2)
      fp.seek(0)

      try:
        await ctx.send(file=discord.File(fp, filename="roles.json"))
      except (discord.Forbidden, discord.HTTPException):
        print_exc()

  @commands.is_owner()
  @commands.command(name="load", hidden=True)
  async def load_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.load_extension("src.cogs." + cog)

    except Exception:
      await try_react(ctx, "❗")
      fprint(f"Failed to load cogs ({cog})", file=sys.stderr)
      print_exc()

    else:
      await try_react(ctx, "✅")
      fprint(f"Successfully loaded cogs ({', '.join(cogs)})")

  @commands.is_owner()
  @commands.command(name="unload", hidden=True)
  async def unload_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.unload_extension("src.cogs." + cog)

    except Exception:
      await try_react(ctx, "❗")
      fprint(f"Failed to unload cogs ({cog})", file=sys.stderr)
      print_exc()

    else:
      await try_react(ctx, "✅")
      fprint(f"Successfully unloaded cogs ({', '.join(cogs)})")

  @commands.is_owner()
  @commands.command(name="reload", hidden=True)
  async def reload_cogs(self, ctx, *cogs):
    try:
      for cog in cogs:
        ctx.bot.unload_extension("src.cogs." + cog)
        ctx.bot.load_extension("src.cogs." + cog)

    except Exception:
      await try_react(ctx, "❗")
      fprint(f"Failed to reload cog ({cog})", file=sys.stderr)
      print_exc()

    else:
      await try_react(ctx, "✅")
      fprint(f"Successfully reloaded cogs ({', '.join(cogs)})")


def setup(bot):
  bot.add_cog(Owner())
