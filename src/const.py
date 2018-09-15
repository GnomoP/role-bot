#!/usr/bin/env python3

from os import environ
from sys import argv

argv = argv[1:]

TOKEN = environ.get("TOKEN")
REDIS_URL = environ.get("REDIS_URL")

PREFIXES = eval(environ.get("PREFIXES", "['>']"))
DEFAULT_COGS = eval(environ.get("COGS", ["owner", "utility", "roles"]))

BOT = True
SYNC_TIME = 1
CHAR_LIMIT = 2000
