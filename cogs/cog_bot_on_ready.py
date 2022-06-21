import discord
from discord.ext import commands
from bot_config import BotConfig

config = BotConfig.get_config('sentdebot')


class BotOnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Sets up the bot status"""
        print(f"We have logged in as {self.bot.user}")
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                'help(sentdebot)',
                type=discord.ActivityType.watching),
            afk=True)


def setup(bot):
    bot.add_cog(BotOnReady(bot))
