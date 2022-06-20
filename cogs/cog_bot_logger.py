import os
import time

from discord.ext import commands
from bot_config import BotConfig

config = BotConfig.get_config('sentdebot')


class BotLogger(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.msgs = os.path.join(config.path, 'msgs.csv')
        self.log = os.path.join(config.path, 'log.txt')
        print(f'Logger initialized, logging to {self.log}, messages to {self.msgs}')
        # if not exists, create the files
        if not os.path.exists(self.msgs):
            with open(self.msgs, 'w') as f:
                f.write('')
        if not os.path.exists(self.log):
            with open(self.log, 'w') as f:
                f.write('')

    @commands.Cog.listener()
    async def on_message(self, message):
        with open(self.msgs, "a") as msgs, open(f"{config.path}/log.csv", "a") as logs:
            if message.author.id not in [bot.id for bot in config.chatbots]:
                msgs.write(f"{int(time.time())},{message.author.id},{message.channel}\n")
            if message.author.id not in config.chatbots:
                try:
                    logs.write(f"{int(time.time())},{message.author.id},{message.channel},{message.content}\n")
                except Exception as e:
                    logs.write(f"{str(e)}\n")


def setup(bot):
    bot.add_cog(BotLogger(bot))
