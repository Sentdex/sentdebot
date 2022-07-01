"""Cog to add silly bot functions like jokes, etc."""
import asyncio

import requests
import nextcord
from nextcord.ext import commands, tasks


class FunCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='dev_joke()', help='get a silly joke')
    async def dev_joke(self, ctx):
        # get joke from https://backend-omega-seven.vercel.app/api/getjoke
        # send the 'question', wait 1 sec for every 3 words in question, then send the 'punchline'
        joke = requests.get('https://backend-omega-seven.vercel.app/api/getjoke').json()[0]
        print(joke)

        question = joke['question']
        punchline = joke['punchline']

        await ctx.send(question)
        await asyncio.sleep(len(question.split()) // 2)
        await ctx.send(punchline)

    @commands.command(name='zen()', help='get some python zen')
    async def zen(self, ctx):
        await ctx.send("""```return 
    Beautiful is better than ugly.
    Explicit is better than implicit.
    Simple is better than complex.
    Complex is better than complicated.
    Flat is better than nested.
    Sparse is better than dense.
    Readability counts.
    Special cases aren't special enough to break the rules.
    Although practicality beats purity.
    Errors should never pass silently.
    Unless explicitly silenced.
    In the face of ambiguity, refuse the temptation to guess.
    There should be one-- and preferably only one --obvious way to do it.
    Although that way may not be obvious at first unless you're Dutch.
    Now is better than never.
    Although never is often better than right now.
    If the implementation is hard to explain, it's a bad idea.
    If the implementation is easy to explain, it may be a good idea.
    Namespaces are one honking great idea -- let's do more of those!
    —Tim Peters```""")

    @commands.command(name='inspire()', help='get some inspiration')
    async def inspire(self, ctx):
        url = "https://what-to-code.com/api/ideas/random"
        with requests.Session() as s:
            download = s.get(url)
            data = download.json()
            embed = nextcord.Embed(title=data['title'], description=data['description'], color=0x00ff00)
            await ctx.send(embed=embed)


def setup(bot):
    fc = FunCommands(bot)
    bot.add_cog(fc)
