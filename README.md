# role-bot

[![discord.py](https://img.shields.io/pypi/v/discord.py.svg)](https://github.com/Rapptz/discord.py/tree/rewrite) [![Build Status](https://travis-ci.org/andymccurdy/redis-py.svg)](https://github.com/andymccurdy/redis-py)

Bot for listing the avaliable roles in a given Discord server. Written with discord.py (rewrite branch).

## Introduction

The bot is written in discord.py, and it's main purpose is to keep an up-to-date, automatically updated list of the avaliable roles in a given Discord guild, for whatever the reason. The shown roles are completely configurable, as well as the roles required for a given user to update them in the first place.

### Requirements

+ Python 3.5.x or later
  + discord.py (rewrite branch)
  + redis-py
+ One avaliable `worker` Dyno on Heroku

Those requirements are explicit on the [requirements.txt](https://github.com/GnomoP/role-bot/blob/remote/requirements.txt) file and the [Procfile](https://github.com/GnomoP/role-bot/blob/remote/Procfile), and ready for deployment on any Heroku application.

## License

This software is freely avaliable under the [GPLv3 License](https://github.com/GnomoP/role-bot/blob/remote/LICENSE).

## TODO

+ [ ] Properly formatted `help` command.
+ [ ] More organized cogs and methods, with separated modules.
+ [ ] Concatenate `add`, `remove`, `allow` and `unallow` commands in a single `config` command.
