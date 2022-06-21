"""Cog to send a daily dog to the dog channel"""

import io
import aiohttp
import discord
import requests
from discord.ext import commands, tasks


class DailyDog(discord.ext.commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_dog.start()


    @tasks.loop(seconds=86400)
    async def daily_dog(self):
        await self.bot.wait_until_ready()

        dogs_channel = discord.utils.get(self.bot.get_all_channels(), name='dogs')
        if dogs_channel is None:
            return
        # check to see if there was already a daily dog in the last 24 hours
        # get last bot message that starts with "Here's your daily dog!"
        messages = await dogs_channel.history(limit=100).flatten()
        for message in messages:
            if message.content.startswith('Here\'s your daily dog!'):
                return
        # if there was no daily dog in the last 24 hours, send one
        async with aiohttp.ClientSession() as session:
            async with session.get(requests.get('https://dog.ceo/api/breeds/image/random').json()['message']) as resp:
                if resp.status != 200:
                    return await dogs_channel.send('Could not download file...')
                data = io.BytesIO(await resp.read())
                # send here is your daily dog
                await dogs_channel.send("Here's your daily dog!", file=discord.File(data, 'cool_image.png'))


def setup(bot):
    dd = DailyDog(bot)
    bot.add_cog(dd)
