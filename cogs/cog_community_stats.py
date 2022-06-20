from discord.ext import commands


class CommunityStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        def _community_report(guild):
            online = 0
            idle = 0
            offline = 0

            for m in guild.members:
                if str(m.status) == "online":
                    online += 1
                elif str(m.status) == "offline":
                    offline += 1
                else:
                    idle += 1

            return online, idle, offline

    @commands.command(name='member_count()', help='get the member count')
    async def member_count(self, ctx):
        await ctx.send(f'{len([member for member in ctx.guild.members if not member.bot])}')

    @commands.command(name='community_report()', help='get some stats on community')
    async def community_report(self, ctx):
        await ctx.send('This command is not implemented yet')

    @commands.command(name='user_activity()', help='See some stats on top users')
    async def user_activity(self, ctx):
        await ctx.send('This command is not implemented yet')

def setup(bot):
    bot.add_cog(CommunityStats(bot))