from discord.ext import commands

# todo: make it so the file names are not forced to be one word lower case

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # function to turn a classname to a file name
    def class_to_file(self, class_name):
        # we need to split at the capital letters
        cap_indexes = [i for i, char in enumerate(class_name) if char.isupper()]
        # split at the char before caps it > 0 to avoid the first letter and insert an underscore
        file_name = class_name[:cap_indexes[0]] + '_' + class_name[cap_indexes[0]:]
        # lowercase the file name
        file_name = file_name.lower()
        # add cog_ to the file name
        file_name = 'cogs.' + file_name
        return file_name


    @commands.command(name='load_cog()', help='load a cog', hidden=True, aliases=['load_cog'])
    async def load_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            self.bot.load_extension(f'cogs.{self.class_to_file(cog_name)}')
            await ctx.send(f'{cog_name} loaded')
        else:
            await ctx.send('You are not allowed to use this command')

    @commands.command(name='unload_cog()', help='unload a cog', hidden=True, aliases=['unload_cog'])
    async def unload_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            self.bot.unload_extension(f'cogs.{self.class_to_file(cog_name)}')
            await ctx.send(f'{cog_name} unloaded')
        else:
            await ctx.send('You are not allowed to use this command')

    @commands.command(name='reload_cog()', help='reload a cog', hidden=True, aliases=['reload_cog'])
    async def reload_cog(self, ctx, cog_name):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            self.bot.reload_extension(f'cogs.{self.class_to_file(cog_name)}')
            await ctx.send(f'{cog_name} reloaded')
        else:
            await ctx.send('You are not allowed to use this command')

    @commands.command(name='list_cogs()', help='gives a list of loaded extensions', hidden=True)
    async def list_cogs(self, ctx):
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            await ctx.send(f'Loaded cogs: {", ".join(self.bot.cogs)}')
        else:
            await ctx.send('You are not allowed to use this command')

    @commands.command(name='logout()', help='logout', aliases=['gtfo()'], hidden=True)
    async def logout(self, ctx):
        # check to see if the authors' id is the server owners or admins
        print(f'{ctx.author.id} is trying to logout')
        if ctx.author.id == ctx.guild.owner.id or ctx.author.id in ctx.guild.owner.guild_permissions.administrator:
            # todo, restrict bact to server owner
            await ctx.send('Logging out')
            await self.bot.logout()
        else:
            await ctx.send('You are not allowed to use this command')


def setup(bot):
    bot.add_cog(AdminTools(bot))
