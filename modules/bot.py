import discord
import random
import time
import os
import re

# py -3.6 -m pip install --upgrade requests-html
from requests_html import HTMLSession
from matplotlib import style

from .definitions import bot, local_files_path
from .definitions import SENTDEX_ID, SENTEX_GUILD_ID
from .definitions import MAIN_CH_ID, IMAGE_CHAN_IDS, VANITY_ROLE_IDS, CHATBOTS
from .background_tasks import community_report

style.use("dark_background")

commands_available = """```py
def commands():
    return {
        sentdebot.member_count(): 'get member count',
        sentdebot.community_report(): 'get some stats on community',
        sentdebot.search("QUERY"): 'search for a string',
        sentdebot.commands(): 'get commands',
        sentdebot.logout(): 'Sentdex-only command to log Sentdebot off'
        sentdebot.user_activity(): 'See some stats on top users',
    }
```"""


def search_term(message):
    try:
        match = re.fullmatch('sentdebot.search\((["|\'])([^\)]+)(["|\'])\)', message)
        if match.group(1) != match.group(3):
            return False
        for check in re.finditer(match.group(1), match.group(2)):
            if match.group(2)[check.start() - 1] != '\\':
                return False
        return match.group(2)
    except Exception:
        return False


@bot.event  # event decorator/wrapper
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('help(sentdebot)'))


@bot.event
async def on_message(message):
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    sentdex_guild = bot.get_guild(SENTEX_GUILD_ID)
    author_roles = message.author.roles
    # print(author_roles)
    # author_role_ids = [r.id for r in author_roles]

    if random.choice(range(500)) == 30:
        matches = [r for r in author_roles if r.id in VANITY_ROLE_IDS]
        # print(matches)

        if len(matches) == 0:
            try:
                role_id_choice = random.choice(VANITY_ROLE_IDS)
                actual_role_choice = sentdex_guild.get_role(role_id_choice)
                # print(type(message.author))
                author_roles.append(actual_role_choice)
                await message.author.edit(roles=author_roles)
            except Exception as e:
                print('EDITING ROLES ISSUE:', str(e))

    with open(os.path.join(local_files_path, 'msgs.csv'), "a") as f:
        if message.author.id not in CHATBOTS:
            f.write(f"{int(time.time())}, {message.author.id}, {message.channel}\n")

    with open(os.path.join(local_files_path, 'log.csv'), "a") as f:
        if message.author.id not in CHATBOTS:
            try:
                f.write(f"{int(time.time())}, {message.author.id}, {message.channel}, {message.content}\n")
            except Exception as e:
                f.write(f"{str(e)}\n")

    if "sentdebot.member_count()" == message.content.lower():
        await message.channel.send(f"```py\n{sentdex_guild.member_count}```")


    elif "sentdebot.community_report()" == message.content.lower() and message.channel.id in IMAGE_CHAN_IDS:
        online, idle, offline = community_report(sentdex_guild)

        file = discord.File(os.path.join(local_files_path, "online.png"), filename=f"online.png")
        await message.channel.send("", file=file)

        await message.channel.send(
                f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    elif "sentdebot.p6()" == message.content.lower():
        await message.channel.send(
                f"```\nThe Neural Networks from Scratch video series will resume when the NNFS book is completed. This means the videos will resume around Sept or Oct 2020.\n\nIf you are itching for the content, you can buy the book and get access to the draft now. The draft is over 500 pages, covering forward pass, activation functions, loss calcs, backward pass, optimization, train/test/validation for classification and regression. You can pre-order the book and get access to the draft via https://nnfs.io```")

    elif "sentdebot.user_activity()" == message.content.lower() and message.channel.id in IMAGE_CHAN_IDS:  # and len([r for r in author_roles if r.id in admins_mods_ids]) > 0:
        file = discord.File(os.path.join(local_files_path, "activity.png"), filename=f"activity.png")
        await message.channel.send("", file=file)

        # await message.channel.send(f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    elif "help(sentdebot)" == message.content.lower() or "sentdebot.commands()" == message.content.lower():
        await message.channel.send(commands_available)

    # if it doesnt work later.
    # elif "sentdebot.logout()" == message.content.lower() and message.author.id == 324953561416859658:
    elif "sentdebot.logout()" == message.content.lower() and message.author.id == SENTDEX_ID:
        await bot.close()

    elif "sentdebot.gtfo()" == message.content.lower() and message.author.id == SENTDEX_ID:
        await bot.close()

    elif "sentdebot.get_history()" == message.content.lower() and message.author.id == SENTDEX_ID:

        channel = sentdex_guild.get_channel(MAIN_CH_ID)

        async for message in channel.history(limit=999999999999999):
            if message.author.id == SENTDEX_ID:
                with open(os.path.join(local_files_path, "history_out.csv"), "a") as f:
                    f.write(f"{message.created_at},1\n")

    elif message.content.lower().startswith("sentdebot.search"):
        query = search_term(message.content)
        print(f"Query: {query}")
        if query:
            # query = match.group(1)
            print(query)

            qsearch = query.replace(" ", "%20")
            full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
            session = HTMLSession()
            r = session.get(full_link)

            specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if
                                  "collection-item" in tut.html]

            if len(specific_tutorials) > 0:
                return_str = "\n---------------------------------------\n".join(
                        f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
                return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

                await message.channel.send(return_str)
            else:
                await message.channel.send(f"""```py
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NotFoundError: {query} not found```""")
    else:
        await bot.process_commands(message)
