# example cog with example commands
from nextcord.ext import commands

class ExampleCog(commands.Cog, name="Example Cog"):
    def __init__(self, bot):
        self.bot = bot


    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        # execture command
        await self.bot.process_commands(message)