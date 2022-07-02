"""cog to handle nickname management"""
from nextcord.ext import commands


class NicknameManager(commands.Cog, name="Nickname Manager"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        nick = self.bot.config.get('bot_name')
        for guild in self.bot.guilds:
            await guild.me.edit(nick=nick)


def setup(bot):
    bot.add_cog(NicknameManager(bot))
