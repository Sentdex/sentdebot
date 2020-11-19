from discord.ext.commands import Cog, command
# from discord import Embed

class Community:
    @command()
    async def member_count(self, ctx):
        await ctx.send(f"```py\n{ctx.bot.guild.member_count}```")


def setup(bot):
    bot.add_cog(Community)