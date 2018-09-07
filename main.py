#!/usr/bin/env python3

import sys
import traceback
import redis
from src.bot import Bot
from src.utils import fprint
from src.const import BOT, TOKEN, REDIS_URL, DEFAULT_COGS


db = redis.from_url(REDIS_URL)
bot = Bot(db)


if __name__ == "__main__":
  for cog in DEFAULT_COGS:
    try:
      bot.load_extension("src.cogs." + cog)

    except Exception:
      fprint(f"Failed to load cogs ({cog})", file=sys.stderr)
      traceback.print_exc()

bot.run(TOKEN, bot=BOT, reconnect=True)
