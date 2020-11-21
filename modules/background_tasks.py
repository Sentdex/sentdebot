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
from collections import Counter

from .definitions import local_files_path
from .definitions import bot
from .definitions import SENTEX_GUILD_ID
from .definitions import DAYS_BACK, MOST_COMMON_INT, RESAMPLE, DISCORD_BG_COLOR
from .definitions import COMMUNITY_BASED_CHANNELS, HELP_CHANNELS


def community_report(guild):
    """

    Args:
        guild:

    Returns:
        online: int
        idle: int
        offline: int
    """
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
    await bot.wait_until_ready()
    global sentdex_guild
    sentdex_guild = bot.get_guild(SENTEX_GUILD_ID)

    while not bot.is_closed():
        try:
            online, idle, offline = community_report(sentdex_guild)
            metrics_path = os.path.join(local_files_path, "usermetrics.csv")
            with open(metrics_path, "a") as f:
                f.write(f"{int(time.time())},{online},{idle},{offline}\n")

            df_msgs = pd.read_csv(os.path.join(local_files_path, "msgs.csv"),
                                  names=['time', 'uid', 'channel']
                                  )
            df_msgs = df_msgs[(df_msgs['time'] > time.time() - (86400 * DAYS_BACK))]
            df_msgs['count'] = 1
            df_msgs['date'] = pd.to_datetime(df_msgs['time'], unit='s')
            df_msgs.drop("time", 1, inplace=True)
            df_msgs.set_index("date", inplace=True)

            df_no_dup = df_msgs.copy()
            df_no_dup['uid2'] = df_no_dup['uid'].shift(-1)
            df_no_dup['uid_rm_dups'] = list(map(df_match, df_no_dup['uid'], df_no_dup['uid2']))

            df_no_dup.dropna(inplace=True)

            message_volume = df_msgs["count"].resample(RESAMPLE).sum()

            user_id_counts_overall = Counter(
                    df_no_dup[df_no_dup['channel'].isin(COMMUNITY_BASED_CHANNELS)]['uid'].values).most_common(
                    MOST_COMMON_INT)
            # print(user_id_counts_overall)

            uids_in_help = Counter(df_no_dup[df_no_dup['channel'].isin(HELP_CHANNELS)]['uid'].values).most_common(
                    MOST_COMMON_INT)
            # print(uids_in_help)

            df = pd.read_csv(metrics_path, names=['time', 'online', 'idle', 'offline'])
            df = df[(df['time'] > time.time() - (86400 * DAYS_BACK))]
            df['date'] = pd.to_datetime(df['time'], unit='s')
            df['total'] = df['online'] + df['offline'] + df['idle']
            df.drop("time", 1, inplace=True)
            df.set_index("date", inplace=True)

            df = df.resample(RESAMPLE).mean()
            df = df.join(message_volume)

            df.dropna(inplace=True)
            # print(df.head())

            fig = plt.figure(facecolor=DISCORD_BG_COLOR)
            ax1 = plt.subplot2grid((2, 1), (0, 0))
            plt.ylabel("Active Users")
            plt.title("Community Report")
            ax1.set_facecolor(DISCORD_BG_COLOR)
            ax1v = ax1.twinx()
            plt.ylabel("Message Volume")
            # ax1v.set_facecolor(DISCORD_BG_COLOR)
            ax2 = plt.subplot2grid((2, 1), (1, 0))
            plt.ylabel("Total Users")
            ax2.set_facecolor(DISCORD_BG_COLOR)

            ax1.plot(df.index, df.online, label="Active Users\n(Not Idle)")
            # ax1v.bar(df.index, df["count"], width=0.01)

            ax1v.fill_between(df.index, 0, df["count"], facecolor="w", alpha=0.2, label="Message Volume")
            ax1.legend(loc=2)
            ax1v.legend(loc=9)

            ax2.plot(df.index, df.total, label="Total Users")
            ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))

            # for label in ax2.xaxis.get_ticklabels():
            #        label.set_rotation(45)
            ax2.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='lower'))
            ax2.legend()

            plt.subplots_adjust(left=0.11, bottom=0.10, right=0.89, top=0.95, wspace=0.2, hspace=0)
            ax1.get_xaxis().set_visible(False)

            ax1v.set_ylim(0, 3 * df["count"].values.max())

            # plt.show()
            plt.savefig(os.path.join(local_files_path, "online.png"), facecolor=fig.get_facecolor())
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
                        msgs.append(pair[1] / 1.0)
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
                        msgs.append(pair[1] / 1.0)
                    else:
                        msgs.append(pair[1])
                    # users.append(pair[0])
                except Exception as e:
                    print(str(e))

            y_pos = np.arange(len(users))
            ax2.barh(y_pos, msgs, align='center', alpha=0.5)
            plt.yticks(y_pos, users)

            plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)
            plt.savefig(os.path.join(local_files_path, "activity.png"), facecolor=fig.get_facecolor())
            plt.clf()

            await asyncio.sleep(300)

        except Exception as e:
            print(str(e))
            await asyncio.sleep(300)


def start_all_background_tasks():
    bot.loop.create_task(user_metrics_background_task())
