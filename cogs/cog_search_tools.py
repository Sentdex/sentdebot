from discord.ext import commands


# a search query
class SearchTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search()', help='search for a string', args=['QUERY'])
    async def search(self, ctx, query):
        await ctx.send('This command is not implemented yet')

    # function to serach sentdex' youtube channel for a video, send a list of results to the channel
    @commands.command(name='search_youtube()', help='search for a video on youtube', args=['QUERY'])
    async def search_youtube(self, ctx, *query):
        await ctx.send('This command is not implemented yet')


def setup(bot):
    bot.add_cog(SearchTools(bot))
