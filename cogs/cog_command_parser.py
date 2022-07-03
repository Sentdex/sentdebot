"""Cog that handles command parsing for any command that has a query"""
import re

import nextcord as discord
from nextcord.ext import commands
from nextcord.ext.commands import CommandNotFound
from pyston import PystonClient, File
from requests_html import HTMLSession, AsyncHTMLSession

session = AsyncHTMLSession()


class CommandParser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_commands = {
            'search': (self.search, 'search site for query'),
            'search_youtube': (self.search_youtube, 'search youtube for query'),
        }
        print(f'Loaded {self.__class__.__name__}')
        print(f'Loaded commands: {list(self.search_commands.keys())}')

    @commands.Cog.listener()
    async def on_message(self, message):
        def parse(message):
            inp = message.strip()[len(self.bot.config["bot_prefix"]):]
            lparen_idx = inp.find('(')
            func_name = inp[:lparen_idx]
            arg_list_str = inp[lparen_idx + 1:-1]
            arg_list = arg_list_str.split(',')
            return func_name, arg_list

        if message.author.bot:
            return

        if message.content.startswith(self.bot.config["bot_prefix"]):
            func_name, arg_list = parse(message.content)
            self.bot.process_commands(f"{func_name} {' '.join(arg_list)}")

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Function to ignore command not found errors. this is because we are using the same format for both the
        built in commands and the parsed ones, thus whenever you use a command with a query, it logs an error"""
        if isinstance(error, CommandNotFound):
            return
        raise error  # so we don't silently handle all errors

    @staticmethod
    async def search(message, query):
        """Searches the sentdex website for the query"""

        query = query.strip('"').strip("'")
        qsearch = query.replace(" ", "%20")
        full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
        session = HTMLSession()
        r = session.get(full_link)

        specific_tutorials = [(
            tut.text, list(tut.links)[0])
            for tut in r.html.find("a")
            if "collection-item" in tut.html]

        if len(specific_tutorials) > 0:
            return_str = "\n---------------------------------------\n".join(
                f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
            return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

            await message.channel.send(return_str)
        else:
            await message.channel.send(f"""```py
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        NotFoundError: {query} not found```""")

    @staticmethod
    async def search_youtube(message, query):
        """Searches youtube channel for the query"""
        # look on youtube for query
        try:
            query = query.strip('"').strip("'")
            query = query.replace(" ", "%20")
            url = f"https://www.youtube.com/c/sentdex/search?query={query}"
            response = await session.get(url)
            # reply searching
            message = await message.channel.send(f"Searching for '{query}'")
            await response.html.arender(sleep=0.2, scrolldown=1, timeout=60)
            found = response.html.find('a#video-title')
            if len(found) > 0:
                # edit message to add "."
                embeds = []
                for i, links in enumerate(found[:5], 1):
                    await message.edit(content=f"Searching for '{query}'" + "." * i)
                    link = "https://www.youtube.com" + links.attrs['href']
                    text = links.text
                    embeds.append((text, link))
                embed = discord.Embed(title=f"Results")
                for data in embeds:
                    embed.add_field(name=data[0], value=data[1], inline=False)
                await message.edit(content=f"Results for '{query}'", embed=embed)

            else:
                await message.channel.send(f"""```py
            Traceback (most recent call last):
              File "<stdin>", line 1, in <module>
            NotFoundError: {query} not found```""")
        except Exception as e:
            print(e)
            await message.channel.send(f"""```py
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        NotFoundError: {query} not found: {e}```""")
            raise e



    @commands.command("commands()", help="list all commands")
    async def commands_user(self, ctx):
        """Function to print commands"""
        prefix = """```py\ndef commands():\n\treturn {\n"""
        suffix = """\n}\n```"""
        commands_list = []
        for command in sorted(self.bot.commands, key=lambda x: x.name):
            if not command.hidden:
                commands_list.append(f"\t{self.bot.command_prefix}{command.name}: '{command.help}',")
        for command in self.search_commands.keys():
            commands_list.append(
                f"\t{self.bot.command_prefix}{command}('QUERY'): '{self.search_commands[command][1]}',")
        commands_list = "\n".join(commands_list)
        await ctx.send(prefix + commands_list + suffix)

    @commands.command("commands_admin()", help="list all commands")
    @commands.has_permissions(administrator=True)
    async def command_admin(self, ctx):
        """Function to print commands"""
        prefix = """```py\ndef commands():\n\treturn {\n"""
        suffix = """\n}\n```"""
        commands_list = []
        for command in sorted(self.bot.commands, key=lambda x: x.name):
            commands_list.append(f"\t{self.bot.command_prefix}{command.name}: '{command.help}',")
        for command in self.search_commands.keys():
            commands_list.append(
                f"\t{self.bot.command_prefix}{command}('QUERY'): '{self.search_commands[command][1]}',")
        commands_list = "\n".join(commands_list)
        try:
            await ctx.message.delete()
            await ctx.author.send(prefix + commands_list + suffix)
        except discord.Forbidden:
            await ctx.send(f'{ctx.author.mention} I do not have permission to send messages in {ctx.channel.mention}')


def setup(bot):
    bot.add_cog(CommandParser(bot))
