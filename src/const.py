#!/usr/bin/env python3

from os import environ
from sys import argv

argv = argv[1:]

TOKEN = environ.get("TOKEN")
PREFIXES = environ.get("PREFIXES")
REDIS_URL = environ.get("REDIS_URL")

BOT = True
SYNC_TIME = 1
CHAR_LIMIT = 2000

DEFAULT_COGS = ["owner", "utility", "roles"]