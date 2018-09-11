#!/usr/bin/env python3

from traceback import print_exc
import discord
from discord.ext import commands
from src.utils import fprint, oauth_url


class Utility:
  @commands.command()
  async def invite(self, ctx):
    try:
      perms = discord.Permissions(8)
      await ctx.send(oauth_url(ctx.bot.user.id, perms))

    except Exception:
      fprint(f"Cannot send OAuth link to {ctx.author.name}#{ctx.author.discriminator} ({ctx.author.id})")
      print_exc()

  @commands.command()
  async def ping(self, ctx):
    try:
      latency = "{0:.3f}".format(ctx.bot.latency / 1000)
      if not float(latency):
        await ctx.send(f"No latency! (0ms)")
      else:
        await ctx.send(f"Pong! ({latency}ms)")

    except Exception:
      print_exc()


def setup(bot):
  bot.add_cog(Utility())
