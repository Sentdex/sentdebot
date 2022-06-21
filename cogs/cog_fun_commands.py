"""Cog to add silly bot functions like jokes, etc."""
import asyncio
import requests
from discord.ext import commands, tasks


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




def setup(bot):
    fc = FunCommands(bot)
    bot.add_cog(fc)
