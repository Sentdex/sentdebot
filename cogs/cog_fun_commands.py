import asyncio
import io

import aiohttp
import discord
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

    @commands.command(name='get_dog()', help='get a random joke')
    async def get_dog(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get(requests.get('https://dog.ceo/api/breeds/image/random').json()['message']) as resp:
                if resp.status != 200:
                    return await ctx.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                await ctx.send(file=discord.File(data, 'cool_image.png'))


    # function to send a daily dog the the dogs channel
    @tasks.loop(seconds=86400)
    async def daily_dog(self):
        await self.bot.wait_until_ready()

        dogs_channel = discord.utils.get(self.bot.get_all_channels(), name='dogs')
        if dogs_channel is None:
            return
        async with aiohttp.ClientSession() as session:
            async with session.get(requests.get('https://dog.ceo/api/breeds/image/random').json()['message']) as resp:
                if resp.status != 200:
                    return await dogs_channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                # send here is your daily dog
                await dogs_channel.send("Here's your daily dog!", file=discord.File(data, 'cool_image.png'))


def setup(bot):
    fc = FunCommands(bot)
    bot.add_cog(fc)
    fc.daily_dog.start()
