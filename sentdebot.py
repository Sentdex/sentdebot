import os

import discord
from discord.ext import commands

from bot_config import BotConfig


bot_config: BotConfig = BotConfig.get_config('sentdebot')
client = commands.Bot(command_prefix=bot_config.prefix, intents=discord.Intents.all())

# if .replit.txt exists token = token = os.environ['token'] else bot_config.token
if os.path.exists('.replit'):
    token = os.environ['token']
else:
    token = bot_config.token


# drop the help command
client.remove_command('help')



if not os.path.exists('cogs'):
    os.makedirs('cogs')
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')



client.run(token)
