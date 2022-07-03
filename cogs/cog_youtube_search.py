from nextcord.ext import commands


class YouTubeSearch(commands.Cog, name="Search Youtube"):
    pass

def setup(bot):
    bot.add_cog(YouTubeSearch(bot))
