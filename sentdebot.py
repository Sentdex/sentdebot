import os
import random

import discord
from discord.ext import commands, tasks
from requests_html import HTMLSession

from bot_definitions import *
from bot_config import *

bot_config: BotConfig = get_config('sentdebot')
client = commands.Bot(command_prefix=bot_config.prefix, intents=discord.Intents.all())

# drop the help command
client.remove_command('help')


@client.event
async def on_message(message):
    # print raw message
    print(f'{message.author}: {message.content}')
    if message.author == client.user:
        return

    elif message.content.startswith(bot_config.prefix):
        await client.invoke(message)


@client.command(name='commands()', help='get commands', aliases=['help()'])
async def commands(ctx):
    await ctx.send(
        "```py\ndef commands():\n\treturn {\n\t\t" +
        ",\n\t\t".join(
            f'{command.name}: "{command.help}"'
            for command
            in client.commands)[:-1]
        + "\n\t}\n```"
    )


@client.command(name='logout()', help='logout', aliases=['gtfo()'])
async def logout(ctx):
    await ctx.send('Logging out...')
    await client.logout()



# check to see if cogs folder exists
if not os.path.exists('cogs'):
    os.makedirs('cogs')
# load cogs
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

client.run(bot_config.token)
