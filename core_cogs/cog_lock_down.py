"""cog to initiate a server lockdown"""
# block all users except certain roles from sending messages

from nextcord.ext import commands


class LockDown(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lockdown_channel", aliases=["ld"])
    @commands.has_permissions(administrator=True)
    async def lockdown(self, ctx, channel=None):
        # if channel == None, lockdown the current channel
        if channel is None:
            channel = ctx.channel
        else:
            channel = self.bot.get_channel(self.bot.guilds[0], channel.replace("#", ""))

        if channel.permissions_for(ctx.guild.default_role).send_messages:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            await ctx.send(f"{channel.mention} is now locked down.")
        else:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            await ctx.send(f"{channel.mention} is now unlocked.")


def setup(bot):
    bot.add_cog(LockDown(bot))