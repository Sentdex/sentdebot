"""cog to collect news from several sources and send them to the bot as formatted embed"""
from datetime import datetime
from nextcord.ext import commands



class NewsCollector(commands.Cog, name="News Gazette"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="news",
                      help="collect news from several sources and send them to the bot as formatted embed")
    async def news(self, ctx):
        await ctx.send("This is the NewsCollector cog. It is currently in development.")
        await ctx.send("Please contact the developer if you have any questions.")

def setup(bot):
    bot.add_cog(NewsCollector(bot))