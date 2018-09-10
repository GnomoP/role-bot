#!/usr/bin/env python3

from discord.ext import commands


class Fun:
  @commands.is_owner()
  @commands.command(hidden=True)
  async def say(self, ctx, *, message: str="gosei no debaixo"):
    print(message)

    try:
      await ctx.message.delete()
      await ctx.send(" ".join(message))
    except Exception:
      try:
        await ctx.message.add_reaction("😭")
      except Exception:
        pass


def setup(bot):
  bot.add_cog(Fun())
