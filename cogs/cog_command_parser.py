import re

import discord
import requests
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from requests import Response
from requests_html import HTMLSession
import urllib.request

from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')




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
        if message.author != self.bot.user:
            # get content
            content = message.content
            print(f'{message.author} said: {content}')
            # if starts with prefix
            if content.startswith(self.bot.command_prefix):
                print("It's a command")
                # trim prefix
                content = content[len(self.bot.command_prefix):]
                query_start = content.find('(')
                query_end = content.find(')')
                command_name = content[:query_start]
                print(f'Command name: {command_name}')
                if command_name in self.search_commands.keys():
                    print(f'Command name: {command_name} is a search command')
                    args = content[query_start + 1:query_end]
                    print(f'{command_name} {args}')
                    func = self.search_commands[command_name][0]
                    await func(message, args)
                    return True
                else:
                    # process command
                    print(f'Command name: {command_name} is not a search command')
        return False

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, CommandNotFound):
            return
        raise error

    async def search(self, message, query):
        query = query.strip('"').strip("'")
        print(query)
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
        # look on youtube for query
        query = query.strip('"').strip("'")
        query = query.replace(" ", "%20")
        search_url = f"https://www.youtube.com/results?search_query={query}"
        r = urllib.request.urlopen(search_url)
        html = r.read().decode('utf-8')
        print(html.find('yt-lockup-title'))














def setup(bot):
    bot.add_cog(CommandParser(bot))
