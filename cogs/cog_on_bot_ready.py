import discord
from discord.ext import commands

from sentdebot import bot_config


class BotOnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"We have logged in as {self.bot.user}")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game('help(sentdebot)'))
        channel = self.bot.get_channel(bot_config.channels[0].id)
        await channel.send('Hello world!')


def setup(bot):
    bot.add_cog(BotOnReady(bot))