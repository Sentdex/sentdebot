import time

import discord
from discord.ext import commands

from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')


class LoggingTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        with open(f"{bot_config.path}/msgs.csv", "a") as msgs, open(f"{bot_config.path}/logs.csv", "a") as log:
            try:
                if not message.author.bot:
                    msgs.write(f"{int(time.time())},{message.author.id},{message.channel}\n")
                    log.write(f"{int(time.time())},{message.author.id},{message.channel},{message.content}\n")

            except Exception as e:
                log.write(f"{str(e)}\n")

def setup(bot):
    bot.add_cog(LoggingTools(bot))
