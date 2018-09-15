#!/usr/bin/env python3

import json
import tempfile
from traceback import print_exc
from operator import itemgetter
import discord
from discord.ext import commands
from src.utils import get_guild_role, guild_config, has_permissions
from src.utils import try_react, try_delete


class RankedRoles:
  @commands.command()
  async def rank(self, ctx, *, guild_id: int=0):
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

    roles = []
    config = {}

    for role in guild_config(ctx.bot.db, guild.id).get("roles", []):
      rank = 0

      for member in guild.members:
        if get_guild_role(guild, role) in member.roles:
          rank += 1

      config[role] = rank

    def predicate(role, rank):
      role = get_guild_role(guild, role)

      if isinstance(role, discord.Role) and role.name != "@everyone":
        return {"rank": rank, "id": role.id, "name": role.name}
      else:
        return None

    for key, val in config.items():
      role = predicate(key, val)
      if role:
        roles += [role]

      roles = sorted(roles, key=itemgetter("rank"), reverse=True)

    with tempfile.TemporaryFile(mode="w+", encoding="utf-8") as fp:
      json.dump(roles, fp, sort_keys=True, indent=2)
      fp.seek(0)

      try:
        await ctx.send(file=discord.File(fp, filename="rank.json"))
      except (discord.Forbidden, discord.HTTPException):
        print_exc()


def setup(bot):
  bot.add_cog(RankedRoles())