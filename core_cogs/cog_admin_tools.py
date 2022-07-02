"""Cog to handle admin tools, such as reloading cogs, restarting and logging out the bot."""
import nextcord
from nextcord.ext import commands


# todo: make it so the file names are not forced to be one word lower case

class AdminTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def class_to_file(class_name):
        """Function to convert from Cog class name to a cog file name"""
        cap_indexes = [i for i, char in enumerate(class_name) if char.isupper()]
        for i in cap_indexes:
            if i == 0:
                class_name = class_name[:i] + class_name[i].lower() + class_name[i + 1:]
            else:
                class_name = class_name[:i] + '_' + class_name[i].lower() + class_name[i + 1:]
        return "cog_" + class_name

    @staticmethod
    def file_to_class(file_name):
        """Function to convert from cog file name to a Cog class name"""
        # remove 'cog.cog' from the start of the file name
        # switch from camel_case to PascalCase
        file_name = file_name[8:]
        to_strip_indexes = [i for i, char in enumerate(file_name) if char == '_']
        to_upper_indexes = [i + 1 for i, char in enumerate(file_name) if char == '_']
        output_string = ''
        for i in range(len(file_name)):
            if i in to_strip_indexes:
                pass
            elif i in to_upper_indexes:
                output_string += file_name[i].upper()
            else:
                output_string += file_name[i]
        return output_string

    @commands.command(name='load_cog', help='load a cog', hidden=True)
    @commands.has_permissions(administrator=True)
    async def load_cog(self, ctx, cog_name):
        """Load a cog"""
        self.bot.load_extension(f'cogs.{self.class_to_file(cog_name)}')
        await ctx.send(f'{cog_name} loaded')

    @commands.command(name='unload_cog', help='unload a cog', hidden=True)
    @commands.has_permissions(administrator=True)
    async def unload_cog(self, ctx, cog_name):
        """Unload a cog"""
        self.bot.unload_extension(f'cogs.{self.class_to_file(cog_name)}')
        await ctx.send(f'{cog_name} unloaded')

    @commands.command(name='reload_cog', help='reload a cog')
    @commands.has_permissions(administrator=True)
    async def reload_cog(self, ctx, cog_name):
        self.bot.reload_extension(f'cogs.{self.class_to_file(cog_name)}')
        await ctx.send(f'{cog_name} reloaded')

    @commands.command(name='list_cogs', help='gives a list of loaded extensions', hidden=True)
    @commands.has_permissions(administrator=True)
    async def list_cogs(self, ctx):
        # embed a list of loaded cogs
        embed = nextcord.Embed(title='Loaded cogs', color=0x00ff00)
        for extension in self.bot.extensions:
            embed.add_field(
                name=self.file_to_class(extension),
                value=self.bot.extensions[extension].__doc__
                if self.bot.extensions[extension].__doc__
                else 'No description',
                inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='logout', help='logout', aliases=['gtfo'], hidden=True)
    @commands.is_owner()
    async def logout(self, ctx):
        """logout bot"""
        await ctx.send('Logging out')
        self.bot.logout()

    @commands.command(name='restart', help='restart', aliases=['restart_bot'], hidden=True)
    @commands.is_owner()
    async def restart(self, ctx):
        """restart bot"""
        await ctx.send('Restarting')
        await self.bot.logout()
        await self.bot.start(self.bot.token)
        for cog in self.bot.cogs:
            self.bot.reload_extension(f'cogs.{cog}')
        await ctx.send('Restarted')


def setup(bot):
    bot.add_cog(AdminTools(bot))
