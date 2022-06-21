import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands, tasks


class DailyChallenge(commands.Cog):
    # a cog to download the daily challenge from project euler
    def __init__(self, bot):
        self.bot = bot


    def get_daily_challenge(self):
        soup = BeautifulSoup(requests.get('https://projecteuler.net/recent').text, 'html.parser')
        href = soup.find('table', {'id': 'problems_table'}).find_all('tr')[1].find('a')['href']
        return f'https://projecteuler.net/{href}'

    # daily loop
    @tasks.loop(seconds=86400)
    async def daily_challenge(self):
        await self.bot.wait_until_ready()
        channels = discord.utils.get(self.bot.get_all_channels(), name='daily-challenge')
        if channels is None:
            return
        challenge = self.get_daily_challenge()
        for channel in channels:
            messages = await channel.history(limit=100).flatten()
            for message in messages:
                if message.author == self.bot.user:
                    if message.content.startswith('Here is your daily challenge!'):
                        return
            await channel.send(f'Here is your daily challenge! {challenge}')


def setup(bot):
    dc = DailyChallenge(bot)
    bot.add_cog(dc)
    dc.daily_challenge.start()
