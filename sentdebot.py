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

anti_abi_complex_tool = [
    "No flirting Abi!",
    "Abi, please don't give me a complex, I implore you!",
    "!!!!",
    "Sentdebot has stopped responding, reason: Abi Broke me!",
    "X_X",
]


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.change_presence(status=discord.Status.online, activity=discord.Game('help(sentdebot)'))
    channel = client.get_channel(bot_config.channels[0].id)
    await channel.send('Hello world!')
    # get context of the channel
    await commands(channel)


@client.event
async def on_message(message):
    # print raw message
    print(f'{message.author}: {message.content}')
    if message.author == client.user:
        return

    elif message.content.startswith(bot_config.prefix):
        await client.invoke(message)

    else:  # todo remove this tease
        if message.author.id == 255914286533050368:
            if random.randint(0, 10) == 5:
                await message.channel.send(f'{message.author.mention} {random.choice(anti_abi_complex_tool)}')


@client.command(name='member_count()', help='get the member count')
async def member_count(ctx):
    await ctx.send(f'{len([member for member in ctx.guild.members if not member.bot])}')


@client.command(name='community_report()', help='get some stats on community')
async def community_report(ctx):
    await ctx.send('This command is not implemented yet')


@client.command(name='user_activity()', help='See some stats on top users')
async def user_activity(ctx):
    await ctx.send('This command is not implemented yet')


# a search query
@client.command(name='search()', help='search for a string', args=['QUERY'])
async def search(ctx, query):
    await ctx.send('This command is not implemented yet')


@client.command(name='commands()', help='get commands', aliases=['help()'])
async def commands(ctx):
    await ctx.send(
        "```py\ndef commands():\n\treturn {\n\t\t" +
        ",\n\t\t".join(
            f'{command.name}(): "{command.help}"'
            for command
            in client.commands)[:-1]
        + "\n\t}\n```"
    )


@client.command(name='logout()', help='logout', aliases=['gtfo()'])
async def logout(ctx):
    await ctx.send('Logging out...')
    await client.logout()


# function to serach sentdex' youtube channel for a video, send a list of results to the channel
@client.command(name='search_youtube()', help='search for a video on youtube', args=['QUERY'])
async def search_youtube(ctx, *query):
    query = ' '.join(query)
    print(f"searching youtube for: {query}")
    channel_id = 'UCfzlCWGWYyIQ0aLC5w48gBQ'
    # create a session
    session = HTMLSession()
    # search channel for strings matching the query
    r = session.get(f'https://www.youtube.com/results?search_query={query}&channel={channel_id}')
    # create a ist of results
    results = r.html.find('.yt-lockup-title a')
    # create a list of urls
    urls = [f'https://www.youtube.com{result.attrs["href"]}' for result in results]
    # send the list of urls to the channel
    await ctx.send('\n'.join(urls))

# run client
client.run(bot_config.token)


def _community_report(guild):
    online = 0
    idle = 0
    offline = 0

    for m in guild.members:
        if str(m.status) == "online":
            online += 1
        elif str(m.status) == "offline":
            offline += 1
        else:
            idle += 1

    return online, idle, offline