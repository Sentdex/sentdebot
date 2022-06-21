import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from pyston import PystonClient, File
from requests_html import HTMLSession, AsyncHTMLSession

from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')


class CommandParser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_commands = {
            'search': (self.search, 'search site for query'),
            'search_youtube': (self.search_youtube, 'search youtube for query'),
            'eval': (self.eval, 'evaluate code')
        }
        print(f'Loaded {self.__class__.__name__}')
        print(f'Loaded commands: {list(self.search_commands.keys())}')

    @commands.Cog.listener()
    async def on_message(self, message):
        """Listens for messages and parses them for commands"""
        if message.author != self.bot.user:
            content = message.content
            if content.startswith(self.bot.command_prefix):
                content = content[len(self.bot.command_prefix):]
                query_start = content.find('(')
                # get last instance of ')'
                query_end = content.rfind(')')
                command_name = content[:query_start]
                if command_name in self.search_commands.keys():
                    args = content[query_start + 1:query_end]
                    func = self.search_commands[command_name][0]
                    await func(message, args)
                    return True
        return False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Function to ignore command not found errors. this is because we are using the same format for both the
        built in commands and the parsed ones, thus whenever you use a command with a query, it logs an error"""
        if isinstance(error, CommandNotFound):
            return
        raise error  # so we don't silently handle all errors

    @commands.command("commands()", help="list all commands")
    async def commands(self, ctx):
        """Function to print commands"""
        prefix = """```py\ndef commands():\n\treturn {\n"""
        suffix = """\n}\n```"""
        commands_list = []
        admin_commands_list = []
        # add bot commands if not hidden
        for command in self.bot.commands:
            # if not hidden, or author not admin
            if not command.hidden:
                # bot prefix commandname: help
                commands_list.append(f"\t{self.bot.command_prefix}{command.name}: '{command.help}',")
            elif ctx.author.guild_permissions.administrator:
                admin_commands_list.append(f"\t{self.bot.command_prefix}{command.name}: '{command.help}',")
        # add search commands
        for command in self.search_commands.keys():
            # bot prefix commandname: help
            commands_list.append(
                f"\t{self.bot.command_prefix}{command}('QUERY'): '{self.search_commands[command][1]}',")
        commands_list = "\n".join(commands_list)
        admin_commands_list = "\n".join(admin_commands_list)
        # if admin message author, else message channel
        try:
            if ctx.author.guild_permissions.administrator:
                await ctx.author.send(prefix + commands_list + admin_commands_list + suffix)
            await ctx.send(prefix + commands_list + suffix)
        except discord.Forbidden:
            await ctx.send(f'{ctx.author.mention} I do not have permission to send messages in {ctx.channel.mention}')

    async def search(self, message, query):
        """Searches the sentdex website for the query"""
        query = query.strip('"').strip("'")
        qsearch = query.replace(" ", "%20")
        full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
        session = HTMLSession()
        r = session.get(full_link)

        specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if
                              "collection-item" in tut.html]

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

    async def search_youtube(self, message, query):
        """Searches youtube channel for the query"""
        # look on youtube for query
        try:
            session = AsyncHTMLSession()

            query = query.strip('"').strip("'")
            query = query.replace(" ", "%20")
            # url = f"https://www.youtube.com/results?search_query={query}"
            url = f"https://www.youtube.com/c/{bot_config.yt_channel_id}/search?query={query}"
            print(url)
            response = await session.get(url)
            await response.html.arender(sleep=1, keep_page=True, scrolldown=1, timeout=30)
            found = response.html.find('a#video-title')
            if len(found) > 0:
                for links in found[:5]:
                    link = next(iter(links.absolute_links))
                    # find embed link
                    # make discord watchable embed with title, description, and thumbnail
                    embed = discord.Embed(title=links.text, description=links.text, url=link, color=0x00ff00)
                    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{link.split('=')[1]}/0.jpg")
                    await message.channel.send(embed=embed)
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
        NotFoundError: {query} not found```""")


    async def eval(self, message, code):
        """Evaluates code"""
        try:
            client = PystonClient() #  new client for each eval so no pollution
            code = code.strip('"').strip("'").strip('```')
            # first word is language
            lang = code.split('\n')[0].split(' ')[0]
            code = code[len(lang) + 1:]
            if len(code) > 265:
                # tell user code is too long
                await message.channel.send(f"""```py
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
            SyntaxError: {code} is too long```""")
                return

            print(code)
            output = await client.execute(lang, [File(code)])

            await message.channel.send(f"```py\n{output}\n```")
        except Exception as e:
            print(e)
            await message.channel.send(f"""```py
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
        {e}```""")





def setup(bot):
    bot.add_cog(CommandParser(bot))
