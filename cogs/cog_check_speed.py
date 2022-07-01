import nextcord
from nextcord.ext import commands
class CheckSpeed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='check_latency()', help='check the speed of the bot')
    async def check_latency(self, ctx):
        await ctx.send(f'```py\n {round(self.bot.latency * 1000)}ms```')

def setup(bot):
    bot.add_cog(CheckSpeed(bot))