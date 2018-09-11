#!/usr/bin/env python3

import traceback
from os import path
from sys import argv, stderr
from subprocess import check_call, CalledProcessError


def git(*args):
  print("> Running: git", *args)
  return check_call(["git"] + list(args))


DEFAULT_BRANCH = "remote"


__doc__ = (
  "usage: {0} <command>\n"
  "       {0} [-A | --add-all] [-v | --verbose] [-P | --push] [-t | --tail]\n"
  "       {1} [-c | --checkout] <branch> [-m | --commit] <message>\n"
  "       {0} [-h | --help]\n"
  "\n"
  "The following commands are listed in the order of their execution in the\n"
  "script. When the parameters for the commit and checkout commands are missing,\n"
  "the script will exit with status code 1. If they start with a dash ('-'), the\n"
  "command is simply ignored. Without a given checkout branch, it defaults to the\n"
  "'{2}' branch for use in other commands, such as 'push' and 'status'.\n"
  "\n"
  "Commands:\n"
  "  -c, --checkout [branch]    Does a checkout to a new branch with\n"
  "                             `git checkout -b [branch]`\n"
  "  -A, --add_all              Adds all changes done locally with `git add -A`\n"
  "  -m, --commit [message]     Commits the changes with `git commit -m [message]`\n"
  "  -P, --push                 Push to branch with `git push heroku [branch]`\n"
  "  -v, --verbose              Checks the status with `git status -b [branch]`\n"
  "  -t, --tail                 Tails the heroku log\n"
  "  -h, --help                 Displays this help text and exits."
).format(path.split(__file__)[1], " " * len(path.split(__file__)[1]), DEFAULT_BRANCH)

commands = {
  "checkout": False,
  "add_all": False,
  "commit": False,
  "status": False,
  "push": False,
  "tail": False
}

if len(argv) > 1:
  for i, arg in enumerate(argv[1:]):
    if arg in ("-h", "--help"):
      print(__doc__)
      exit(0)

    if arg in ("-A", "--add-all"):
      commands["add_all"] = True
      continue
    if arg in ("-v", "--verbose"):
      commands["status"] = True
      continue
    if arg in ("-P", "--push"):
      commands["push"] = True
      continue
    if arg in ("-t", "--tail"):
      commands["tail"] = True
      continue

    if arg in ("-c", "--checkout"):
      commands["checkout"] = True
      try:
        commands["checkout_branch"] = argv[i + 2]
        assert not commands["checkout_branch"].startswith("-")
      except IndexError:
        print("No checkout branch was given.", file=stderr)
        exit(1)
      except AssertionError:
        commands["checkout"] = False
        commands.pop("checkout_branch")
      continue

    if arg in ("-m", "--commit"):
      commands["commit"] = True
      try:
        commands["commit_message"] = argv[i + 2]
        print(commands.get("commit_message"))
        assert not commands["commit_message"].startswith("-")
      except IndexError:
        print("No commit message was given.", file=stderr)
        exit(1)
      except AssertionError:
        commands["commit"] = False
        commands.pop("commit_message")
      continue

for cmd in commands.values():
  if cmd:
    break
else:
  print("No commands passed. Seek --help", file=stderr)
  exit(0)

try:
  git("checkout", commands.get("checkout_branch", DEFAULT_BRANCH))
except CalledProcessError as e:
  if e.returncode not in (0, 1):
    traceback.print_exc()
    exit(e.returncode)

if commands.get("add_all"):
  try:
    git("add", "-A")
  except CalledProcessError as e:
    if e.returncode not in (0, 1):
      traceback.print_exc()
      exit(e.returncode)

if commands.get("commit"):
  try:
    git("commit", "-m", commands.get("commit_message", "Commit message"))
  except CalledProcessError as e:
    if e.returncode not in (0, 1):
      traceback.print_exc()
      exit(e.returncode)

if commands.get("status"):
  try:
    git("status", "-b", commands.get("checkout_branch", DEFAULT_BRANCH))
  except CalledProcessError as e:
    if e.returncode not in (0, 1):
      traceback.print_exc()
      exit(e.returncode)

if commands.get("push"):
  try:
    branch = commands.get("checkout_branch", DEFAULT_BRANCH)
    if branch != DEFAULT_BRANCH:
      branch = branch + ":" + DEFAULT_BRANCH
    git("push", "heroku", branch)
  except CalledProcessError as e:
    if e.returncode not in (0, 1):
      traceback.print_exc()
      exit(e.returncode)

if commands.get("tail"):
  try:
    check_call(["heroku", "logs", "-t"])
  except KeyboardInterrupt:
    exit(0)
  except CalledProcessError as e:
    if e.returncode not in (0, 1):
      traceback.print_exc()
      exit(e.returncode)
