import logging
import pathlib

import discord

from bot import SentdeBot, get_intents

# Optionally get uvloop for higher performance
try:
    import uvloop  # type: ignore
except ImportError:
    pass
else:
    import asyncio
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)s: %(message)s", level=logging.INFO, datefmt="[%a, %d %B %Y %X]")

Bot = SentdeBot(
    command_prefix = ("sentdebot", "sb"),
    case_insensitive = True,
    intents = get_intents(),
    status = discord.Status.online,
    activity = discord.Game('help(sentdebot)'),
    file_path = pathlib.Path(__file__).parent / "sentdebot"
)

with open(Bot.path / "token.txt", "r") as r:
    token = r.read().split('\n')[0]

if __name__ == "__main__":
    Bot.run(token)
