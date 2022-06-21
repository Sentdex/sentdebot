import os

import discord
from discord.ext import commands

from bot_config import BotConfig

bot_config: BotConfig = BotConfig.get_config('sentdebot')

client = commands.Bot(command_prefix=bot_config.prefix, case_insensitive=False, intents=discord.Intents.all())

client.remove_command('help')

if not os.path.exists('cogs'):
    os.makedirs('cogs')
for filename in os.listdir('./cogs'):
    if filename.startswith("cog_") and filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(bot_config.token)
