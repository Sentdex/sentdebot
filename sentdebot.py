import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import asyncio
import discord
import pandas as pd
import random
import numpy as np
import time
import os
import re

# py -3.6 -m pip install --upgrade requests-html
from requests_html import HTMLSession
from collections import Counter
from matplotlib import style

style.use("dark_background")


path = '/sentdebot/'

# days of history to work with
DAYS_BACK = 21
RESAMPLE = "60min"
# when doing counters of activity, top n users.
MOST_COMMON_INT = 10
# names of channels where we want to count activity.
COMMUNITY_BASED_CHANNELS = ["__main__",
                            "main",
                            "help",
                            "help_0",
                            "help_1",
                            "help_2",
                            "help_3",
                            "voice-channel-text",
                            "__init__",
                            "hello_technical_questions",
                            "help_overflow",
                            "dogs",
                            "show_and_tell","politics_enter_at_own_risk"]

HELP_CHANNELS = ["help",
                 "hello_technical_questions",
                 "help_0",
                 "help_1",
                 "help_2",
                 "help_3",
                 "help_overflow"]

DISCORD_BG_COLOR = '#36393E'

intents = discord.Intents.all()

client = discord.Client(intents=intents)

token = open(f"{path}/token.txt", "r").read().split('\n')[0]

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

image_chan_ids = [408713676095488000,
                  412620789133606914,
                  476412789184004096,
                  499945870473691146,
                  484406428233367562,
                  ]


chatbots = [405511726050574336,
            428904098985803776,
            414630095911780353,
            500507500962119681]


admin_id = 405506750654054401
mod_id = 405520180974714891

admins_mods_ids = [admin_id, mod_id]
# condition to restrict a command to admins/mods: len([r for r in author_roles if r.id in admins_mods_ids]) > 0

vanity_role_ids = [479433667576332289,
                   501115401577431050,
                   501115079572324352,
                   501114732057460748,
                   501115820273958912,
                   501114928854204431,
                   479433212561719296]

channel_ids = [408713676095488000,  # main
               412620789133606914]  # help


def search_term(message):
    try:
        match = re.fullmatch('sentdebot.search\((["|\'])([^\)]+)(["|\'])\)', message)
        if match.group(1) != match.group(3):
            return False
        for check in re.finditer(match.group(1), match.group(2)):
            if match.group(2)[check.start()-1] != '\\':
                return False
        return match.group(2)
    except:
        return False


def community_report(guild):
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


def df_match(c1, c2):
    if c1 == c2:
        return np.nan
    else:
        return c1


async def user_metrics_background_task():
    await client.wait_until_ready()
    global sentdex_guild
    sentdex_guild = client.get_guild(405403391410438165)

    while not client.is_closed():
        try:
            online, idle, offline = community_report(sentdex_guild)
            with open(f"{path}/usermetrics.csv","a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            df_msgs = pd.read_csv(f'{path}/msgs.csv', names=['time', 'uid', 'channel'])
            df_msgs = df_msgs[(df_msgs['time'] > time.time()-(86400*DAYS_BACK))]
            df_msgs['count'] = 1
            df_msgs['date'] = pd.to_datetime(df_msgs['time'], unit='s')
            df_msgs.drop("time", 1,  inplace=True)
            df_msgs.set_index("date", inplace=True)


            df_no_dup = df_msgs.copy()
            df_no_dup['uid2'] = df_no_dup['uid'].shift(-1)
            df_no_dup['uid_rm_dups'] = list(map(df_match, df_no_dup['uid'], df_no_dup['uid2']))

            df_no_dup.dropna(inplace=True)


            message_volume = df_msgs["count"].resample(RESAMPLE).sum()

            user_id_counts_overall = Counter(df_no_dup[df_no_dup['channel'].isin(COMMUNITY_BASED_CHANNELS)]['uid'].values).most_common(MOST_COMMON_INT)
            #print(user_id_counts_overall)

            uids_in_help = Counter(df_no_dup[df_no_dup['channel'].isin(HELP_CHANNELS)]['uid'].values).most_common(MOST_COMMON_INT)
            #print(uids_in_help)

            df = pd.read_csv(f"{path}/usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
            df = df[(df['time'] > time.time()-(86400*DAYS_BACK))]
            df['date'] = pd.to_datetime(df['time'],unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1,  inplace=True)
            df.set_index("date", inplace=True)

            df = df.resample(RESAMPLE).mean()
            df = df.join(message_volume)

            df.dropna(inplace=True)
            #print(df.head())

            fig = plt.figure(facecolor=DISCORD_BG_COLOR)
            ax1 = plt.subplot2grid((2, 1), (0, 0))
            plt.ylabel("Active Users")
            plt.title("Community Report")
            ax1.set_facecolor(DISCORD_BG_COLOR)
            ax1v = ax1.twinx()
            plt.ylabel("Message Volume")
            #ax1v.set_facecolor(DISCORD_BG_COLOR)
            ax2 = plt.subplot2grid((2, 1), (1, 0))
            plt.ylabel("Total Users")
            ax2.set_facecolor(DISCORD_BG_COLOR)

            ax1.plot(df.index, df.online, label="Active Users\n(Not Idle)")
            #ax1v.bar(df.index, df["count"], width=0.01)

            ax1v.fill_between(df.index, 0, df["count"], facecolor="w", alpha=0.2, label="Message Volume")
            ax1.legend(loc=2)
            ax1v.legend(loc=9)

            ax2.plot(df.index, df.total, label="Total Users")
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))

            #for label in ax2.xaxis.get_ticklabels():
            #        label.set_rotation(45)
            ax2.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='lower'))
            ax2.legend()

            plt.subplots_adjust(left=0.11, bottom=0.10, right=0.89, top=0.95, wspace=0.2, hspace=0)
            ax1.get_xaxis().set_visible(False)

            ax1v.set_ylim(0, 3*df["count"].values.max())

            #plt.show()
            plt.savefig(f"{path}/online.png", facecolor = fig.get_facecolor())
            plt.clf()


            fig = plt.figure(facecolor=DISCORD_BG_COLOR)
            ax1 = plt.subplot2grid((2, 1), (0, 0))

            plt.xlabel("Message Volume")
            plt.title(f"General User Activity (past {DAYS_BACK} days)")
            ax1.set_facecolor(DISCORD_BG_COLOR)

            users = []
            msgs = []
            for pair in user_id_counts_overall[::-1]:
                try:
                    users.append(sentdex_guild.get_member(pair[0]).name)  # get member name from here
                    if "Dhanos" in sentdex_guild.get_member(pair[0]).name:
                        msgs.append(pair[1]/1.0)
                    else:
                        msgs.append(pair[1])
                except Exception as e:
                    print(str(e))
            y_pos = np.arange(len(users))
            ax1.barh(y_pos, msgs, align='center', alpha=0.5)
            plt.yticks(y_pos, users)

            ax2 = plt.subplot2grid((2, 1), (1, 0))
            plt.title(f"Help Channel Activity (past {DAYS_BACK} days)")
            plt.xlabel("Help Channel\nMsg Volume")
            ax2.set_facecolor(DISCORD_BG_COLOR)

            users = []
            msgs = []
            for pair in uids_in_help[::-1]:
                try:
                    users.append(sentdex_guild.get_member(pair[0]).name)  # get member name from here

                    if "Dhanos" in sentdex_guild.get_member(pair[0]).name:
                        msgs.append(pair[1]/1.0)
                    else:
                        msgs.append(pair[1])
                    #users.append(pair[0])
                except Exception as e:
                    print(str(e))

            y_pos = np.arange(len(users))
            ax2.barh(y_pos, msgs, align='center', alpha=0.5)
            plt.yticks(y_pos, users)

            plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)
            plt.savefig(f"{path}/activity.png", facecolor=fig.get_facecolor())
            plt.clf()


            await asyncio.sleep(300)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(300)


@client.event  # event decorator/wrapper
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.change_presence(status = discord.Status.online, activity = discord.Game('help(sentdebot)'))


@client.event
async def on_message(message):
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    sentdex_guild = client.get_guild(405403391410438165)
    author_roles = message.author.roles
    #print(author_roles)
    #author_role_ids = [r.id for r in author_roles]



    if random.choice(range(500)) == 30:
        matches = [r for r in author_roles if r.id in vanity_role_ids]
        #print(matches)

        if len(matches) == 0:
            try:
                role_id_choice = random.choice(vanity_role_ids)
                actual_role_choice = sentdex_guild.get_role(role_id_choice)
                #print(type(message.author))
                author_roles.append(actual_role_choice)
                await message.author.edit(roles=author_roles)
            except Exception as e:
                print('EDITING ROLES ISSUE:',str(e))


    with open(f"{path}/msgs.csv","a") as f:
        if message.author.id not in chatbots:
            f.write(f"{int(time.time())},{message.author.id},{message.channel}\n")

    with open(f"{path}/log.csv","a") as f:
        if message.author.id not in chatbots:
            try:
                f.write(f"{int(time.time())},{message.author.id},{message.channel},{message.content}\n")
            except Exception as e:
                f.write(f"{str(e)}\n")


    if "sentdebot.member_count()" == message.content.lower():
        await message.channel.send(f"```py\n{sentdex_guild.member_count}```")



    elif "sentdebot.community_report()" == message.content.lower() and message.channel.id in image_chan_ids:
        online, idle, offline = community_report(sentdex_guild)

        file = discord.File(f"{path}/online.png", filename=f"{path}/online.png")
        await message.channel.send("", file=file)

        await message.channel.send(f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')
    
    elif "sentdebot.p6()" == message.content.lower():
        await message.channel.send(f"```\nThe Neural Networks from Scratch videos will resume one day. https://nnfs.io```")


    elif "sentdebot.user_activity()" == message.content.lower() and message.channel.id in image_chan_ids:  # and len([r for r in author_roles if r.id in admins_mods_ids]) > 0:

        file = discord.File(f"{path}/activity.png", filename=f"{path}/activity.png")
        await message.channel.send("", file=file)

        #await message.channel.send(f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')



    elif "help(sentdebot)" == message.content.lower() or "sentdebot.commands()" == message.content.lower():
        await message.channel.send(commands_available)

    # if it doesnt work later.
    #elif "sentdebot.logout()" == message.content.lower() and message.author.id == 324953561416859658:
    elif "sentdebot.logout()" == message.content.lower() and str(message.author).lower() == "sentdex#7777":
        await client.close()
    elif "sentdebot.gtfo()" == message.content.lower() and str(message.author).lower() == "sentdex#7777":
        await client.close()

    elif "sentdebot.get_history()" == message.content.lower() and str(message.author).lower() == "sentdex#7777":

        channel = sentdex_guild.get_channel(channel_ids[0])

        async for message in channel.history(limit=999999999999999):
            if message.author.id == 324953561416859658:
                with open(f"{path}/history_out.csv", "a") as f:
                    f.write(f"{message.created_at},1\n")


    else:
        query = search_term(message.content)
        if query:
            #query = match.group(1)
            print(query)


            qsearch = query.replace(" ","%20")
            full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
            session = HTMLSession()
            r = session.get(full_link)

            specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if "collection-item" in tut.html]

            if len(specific_tutorials) > 0:
                return_str = "\n---------------------------------------\n".join(f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
                return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

                await message.channel.send(return_str)
            else:
                await message.channel.send(f"""```py
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NotFoundError: {query} not found```""")


client.loop.create_task(user_metrics_background_task())
client.run(token, reconnect=True)
