from discord.ext import commands

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='load_cog()', help='load a cog', hidden=True)
    async def load_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:

            self.bot.load_extension(f'cogs.{cog_name}')
            await ctx.send(f'{cog_name} loaded')

    @commands.command(name='unload_cog()', help='unload a cog', hidden=True)
    async def unload_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:

            self.bot.unload_extension(f'cogs.{cog_name}')
            await ctx.send(f'{cog_name} unloaded')

    @commands.command(name='reload_cog()', help='reload a cog', hidden=True)
    async def reload_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            self.bot.reload_extension(f'cogs.{cog_name}')

    @commands.command(name='list_cogs()', help='gives a list of loaded extensions', hidden=True)
    async def list_cogs(self, ctx):
        await ctx.send(', '.join(self.bot.extensions))

    @commands.command(name='logout()', help='logout', aliases=['gtfo()'], hidden=True)
    async def logout(self, ctx):
        # check to see if the authors' id is the server owners or admins
        print(f'{ctx.author.id} is trying to logout')
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            # todo, restrict bact to server owner
            await ctx.send('Logging out')
            await self.bot.logout()


def setup(bot):
    bot.add_cog(AdminTools(bot))
