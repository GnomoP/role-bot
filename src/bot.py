#!/usr/bin/env python3

import sys
import traceback
import discord
from discord import abc
from discord.ext import commands
from src.utils import fprint, guild_config
from src.const import PREFIXES, REDIS_URL, CHAR_LIMIT, SYNC_TIME


class Bot(commands.Bot):
  def __init__(self, db, *args, **kwargs):
    prefix = commands.when_mentioned_or(*PREFIXES)
    super().__init__(command_prefix=prefix, *args, **kwargs)

    self.db = db

  async def on_connect(self):
    fprint("Connected to Discord...")
    await self.wait_until_ready()

    fprint(f"Logged in as: {self.user.name}#{self.user.discriminator}")

    if len(self.guilds) > 0:
      guilds = ", ".join([f"\"{g.name}\"" for g in self.guilds[:3]])
      fprint(f"Present on {len(self.guilds)} guilds: {guilds}...")

  async def on_guild_join(self, guild):
    fprint(f"Joined a new guild: '{guild.name}' ({guild.id})")
    guild_config(self.db, guild.id)

  async def on_guild_remove(self, guild):
    fprint(f"Left a guild: '{guild.name}' ({guild.id})")
    self.db.delete(guild.id)

  async def on_command_error(self, ctx, e):
    if type(e).__name__ in ("CommandNotFound", "CheckFailure", "NotOwner"):
      return

    if type(e).__name__ in ("BadArgument", "MissingRequiredArgument"):
      try:
        await ctx.send("`%s`" % e)
      except Exception:
        traceback.print_exc()
      return

    if type(e).__name__ == "CommandInvokeError":
      if type(e.original).__name__ in ("HTTPException", "NotFound"):
        return

      if type(e.original).__name__ == ("ClientException", "Forbidden"):
        try:
          await ctx.send("`%s`" % e)
        except Exception:
          traceback.print_exc()
        return

    fprint(e, file=sys.stderr)

  async def update_roles(self, guild):
    config = guild_config(self.db, guild.id)

    for channel in guild.text_channels:
      if int(channel.id) == config.get("channel", 0):
        break

    else:
      if not guild.me.guild_permissions.manage_channels:
        fprint(f"Couldn't update roles for {guild.name} ({guild.id}):",
                   "Missing permission 'manage_channels'", file=sys.stderr)
        return

      try:
        channel = await guild.create_text_channel("tags")
      except Exception:
        return


    if not guild.me.permissions_in(channel).read_message_history:
      fprint(f"Couldn't update roles for {guild.name} ({guild.id}):",
                 "Missing permission 'read_message_history'", file=sys.stderr)
      return

    async for message in channel.history(limit=500).filter(lambda m: m.author.bot):
      try:
        await message.delete()
      except Exception:
          fprint(f"Failed to delete message ({message}) in role channel", file=sys.stderr)

    if not guild.me.permissions_in(channel).send_messages:
      fprint(f"Couldn't update roles for {guild.name} ({guild.id}):",
                 "Missing permission 'send_messages'", file=sys.stderr)
      return

    roles = {}
    for role in guild.roles:
      if role.id not in config.get("exceptions", []):
        roles[role.position] = (role.id, role.name)

    roles = dict(sorted(roles.items()))

    role = []
    for r in roles.values():
      role.append(r[1])
    role.pop(0)

    tags = ["**"]
    while len(role) > 0:
      if len(tags[-1] + ", " + role[-1]) < (CHAR_LIMIT - 2):
        tags[-1] += ", " + role.pop()
      else:
        tags[-1] += "**"
        tags.append("**")
    else:
      tags[-1] += "**"

    messages = []
    for tag in tags:
      messages += [(await channel.send(content=tag)).id]

    config["messages"] = messages
    config["channel"] = channel.id
    config["roles"] = [role[0] for role in roles.values() if role[0] not in config.get("exceptions", [])]

    guild_config(self.db, guild.id, config)
    fprint(f"Updated roles for \"{guild.name}\" ({guild.id})")
