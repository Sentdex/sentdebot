import discord
from discord.ext import commands
from bot_config import BotConfig

config = BotConfig.get_config('sentdebot')


class BotOnReady(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"We have logged in as {self.bot.user}")
        await self.bot.change_presence(
            status=discord.Status.online,
            activity=discord.Game(
                'help(sentdebot)',
                type=discord.ActivityType.watching),
            afk=True)
        # list of extensions
        channel = self.bot.get_channel(config.channels[0].id)
        await channel.send('Loaded cogs: ' + ', '.join(self.bot.cogs))





def setup(bot):
    bot.add_cog(BotOnReady(bot))
