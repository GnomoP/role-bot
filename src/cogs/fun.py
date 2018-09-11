#!/usr/bin/env python3

import discord
from discord.ext import commands
from src.utils import try_react, try_delete


class Fun:
  @commands.is_owner()
  @commands.command(hidden=True)
  async def say(self, ctx, *, message: str="gosei no debaixo"):
    try:
      await try_delete(ctx.message)
      await ctx.send(message)
    except (discord.HTTPException, discord.Forbidden):
      await try_react(ctx, "😭")


def setup(bot):
  bot.add_cog(Fun())
