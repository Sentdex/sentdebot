"""Cog to logging handler"""
import time
import nextcord
from nextcord.ext import commands, tasks


class LoggingTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.path = "./data/"

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        print(f'{message.created_at} {message.author} {message.content}')
        with open(f"{self.path}msgs.csv", "a") as msgs, open(f"{self.path}logs.csv", "a") as log:
            try:
                if not message.author.bot:
                    msgs.write(f"{int(time.time())},{message.author.id},{message.channel}\n")
                    log.write(f"{int(time.time())},{message.author.id},{message.channel},{message.content}\n")

            except Exception as e:
                log.write(f"{str(e)}\n")


def setup(bot):
    bot.add_cog(LoggingTools(bot))
