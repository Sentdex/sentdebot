from nextcord.ext import commands


class DevTools(commands.Cog):
    pass


def setup(bot):
    bot.add_cog(DevTools(bot))
