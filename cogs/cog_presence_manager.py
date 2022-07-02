import nextcord
from nextcord.ext import commands

class PresenceManager(commands.Cog, name="Presence Manager"):
    def __init__(self, bot):
        self.bot = bot

    # on ready
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=nextcord.Game(name=self.bot.config.get("bot_presence_comment")))


def setup(bot):
    bot.add_cog(PresenceManager(bot))
