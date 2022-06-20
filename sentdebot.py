import os

import discord
from discord.ext import commands

from bot_config import BotConfig

bot_config: BotConfig = BotConfig.get_config('sentdebot')
client = commands.Bot(command_prefix=bot_config.prefix, intents=discord.Intents.all())


@client.event
async def on_message(message):
    # print raw message
    print(f'{message.author}: {message.content}')
    if message.author == client.user:
        return
    # get msg context
    await client.process_commands(message)


@client.command(name='commands_string()', help='get commands_string', aliases=['help()'])
async def commands(ctx):
    prefix = "```py\ndef commands_string():\n\treturn {\n\t\t"
    suffix = "\n\t}\n```"
    commands_string = ",\n\t\t".join(
        f'{command.name}: "{command.help}"'
        for command
        in client.commands)[:-1]

    # add cog commands_string
    for cog in client.cogs:
        for command in client.get_cog(cog).get_commands():
            commands_string += f',\n\t\t{command.name}: "{command.help}"'

    await ctx.send(
        prefix + commands_string + suffix
    )

if not os.path.exists('cogs'):
    os.makedirs('cogs')
for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


client.run(bot_config.token)
