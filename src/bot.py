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

  async def on_guild_role_create(self, role):
    await self.update_roles(role.guild)

  async def on_guild_role_delete(self, role):
    await self.update_roles(role.guild)

  async def on_guild_role_update(self, before, after):
    await self.update_roles(before.guild)

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

    roles = {}
    for role in guild.roles:
      if role.id not in config.get("exceptions", []):
        roles[role.position] = (role.id, role.name)

    roles = dict(sorted(roles.items()))
    roles.pop(0)

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

    tags = [", ".join(f"`{role[1]}`" for role in roles.values())]

    while len(tags[-1]) > CHAR_LIMIT:
      last = tags[-1]

      tags[-1] = last[:CHAR_LIMIT]
      tags.append(last[CHAR_LIMIT:])


    if not guild.me.permissions_in(channel).read_message_history:
      fprint(f"Couldn't update roles for {guild.name} ({guild.id}):",
                 "Missing permission 'read_message_history'", file=sys.stderr)
      return

    for message in config.get("messages", []):
      try:
        m = await channel.get_message(message)
        await m.delete()
      except Exception:
          fprint(f"Failed to delete previous message ({message})", file=sys.stderr)

    if not guild.me.permissions_in(channel).send_messages:
      fprint(f"Couldn't update roles for {guild.name} ({guild.id}):",
                 "Missing permission 'send_messages'", file=sys.stderr)
      return

    messages = []
    for tag in tags:
      messages += [(await channel.send(content=tag)).id]

    config["messages"] = messages
    config["channel"] = channel.id
    config["roles"] = [role[0] for role in roles.values() if role[0] not in config.get("exceptions", [])]

    guild_config(self.db, guild.id, config)
    fprint(f"Updated roles for \"{guild.name}\" ({guild.id})")
