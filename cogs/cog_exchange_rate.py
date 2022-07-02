"""cog to collect exchange rates from https://api.coingecko.com/api/v3/exchange_rates
and send them to the bot as formatted embed"""


import nextcord
from aiohttp import ClientSession
from nextcord.ext import commands, tasks


class ExchangeRate(commands.Cog, name="Exchange Rate"):
    pass


def setup(bot):
    bot.add_cog(ExchangeRate(bot))

