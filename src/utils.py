#!/usr/bin/env python3

import json
import traceback
from os import path
from datetime import datetime

# pylint: disable=W0614
import discord
from discord.utils import get, find, oauth_url
from src.const import REDIS_URL


def fprint(*args, **kwargs):
  return print(datetime.now().strftime("[%H:%M:%S]"), *args, **kwargs)


def guild_config(db, guild_id: int, params: dict={}):
  default = {
    "channel": 0,
    "roles": [],
    "allowed": [],
    "messages": [],
    "exceptions": []
  }

  try:
    config = json.loads(db.get(guild_id))
  except (json.JSONDecodeError, TypeError):
    config = {}
  except Exception:
    config = {}
    traceback.print_exc()
  finally:
    config.update(params)

  try:
    db.set(guild_id, json.dumps(config))
  except json.JSONDecodeError:
    return None
  except Exception:
    traceback.print_exc()
  finally:
    return config or default


def has_permissions(ctx):
  return (
    ctx.channel.permissions_for(ctx.me).manage_roles == True or
    ctx.channel.permissions_for(ctx.me).administrator == True or
    set(guild_config(ctx.bot.db, ctx.guild.id)["allowed"]) & {r.id for r in ctx.author.roles}
  )


async def try_react(ctx, emoji: str):
  try:
    await ctx.message.add_reaction(emoji)
  except (discord.HTTPException, discord.Forbidden):
    return None
  else:
    return True


async def try_delete(message: discord.Message):
  try:
    await message.delete()
  except (discord.HTTPException, discord.Forbidden, discord.NotFound):
    return None
  else:
    return True


async def try_send(ctx: discord.abc.Messageable, *args, **kwargs):
  try:
    await ctx.send(*args, **kwargs)
  except (discord.HTTPException, discord.Forbidden, discord.NotFound):
    return None
  else:
    return True


def get_guild_channel(guild, id):
  if not isinstance(guild, discord.Guild):
    raise TypeError("`guild` is not an instance of `discord.Guild`")

  if isinstance(id, int):
    channel = guild.get_channel(id)

    if isinstance(channel, discord.TextChannel):
      return channel
    else:
      return None

  elif isinstance(id, str):
    try:
      channel = guild.get_channel(int(id))

    except Exception:
      pass

    else:
      if isinstance(channel, discord.TextChannel):
        return channel
      else:
        return None

    try:
      channel = guild.get_channel(int(id[2:-1]))

    except Exception:
      pass

    else:
      if isinstance(channel, discord.TextChannel):
        return channel
      else:
        return None

  else:
    return None


def get_guild_role(guild, id):
  if not isinstance(guild, discord.Guild):
    raise TypeError("`guild` is not an instance of `discord.Guild`")

  for role in guild.roles:
    if isinstance(id, int) and role.id == id:
      break

    if isinstance(id, str):
      if role.name == id:
        break

      try:
        if role.id == int(id):
          break
        if role.id == int(id[3:-1]):
          break

      except Exception:
        pass

  else:
    return None

  return role

