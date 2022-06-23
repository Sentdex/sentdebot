"""Cog to provide a daily challenge to the daily-challenge channel"""
import nextcord as discord
from nextcord.ext import commands, tasks


import requests
from bs4 import BeautifulSoup



class DailyChallenge(commands.Cog):
    # a cog to download the daily challenge from project euler
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(hours=12)
    async def daily_challenge(self):
        await self.bot.wait_until_ready()
        channels = discord.utils.get(self.bot.get_all_channels(), name='daily-challenge')
        if channels is not None:
            soup = BeautifulSoup(requests.get('https://projecteuler.net/recent').text, 'html.parser')
            href = soup.find('table', {'id': 'problems_table'}).find_all('tr')[1].find('a')['href']
            challenge = f'https://projecteuler.net/{href}'
            messages = await channels.history(limit=100).flatten()
            for message in messages:
                if message.author.id == self.bot.user.id:
                    if message.content.startswith('Here\'s your daily challenge!'):
                        return
            async for message in channels.history(limit=100):
                if message.author == self.bot.user:
                    if message.content.startswith('Here is your daily challenge!'):
                        return
            await channels.send("Here is your daily challenge!", embed=discord.Embed(description=challenge))


def setup(bot):
    dc = DailyChallenge(bot)
    bot.add_cog(dc)
    dc.daily_challenge.start()
