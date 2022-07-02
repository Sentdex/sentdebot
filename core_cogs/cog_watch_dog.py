"""cog that monitors the guild for raids and spam, sending messages to admins/moderators"""

from nextcord.ext import commands


class WatchDog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

def setup(bot):
    bot.add_cog(WatchDog(bot))