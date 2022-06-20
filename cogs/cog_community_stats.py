import asyncio
import os
import time
from collections import Counter

from matplotlib import pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates

from bot_definitions import get_all_channels_by_tag

import discord
import numpy as np
import pandas as pd
from discord.ext import commands
from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')


class CommunityStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.user_metrics_background_task(), name='user_metrics_background_task')

    @commands.command(name='member_count()', help='get the member count')
    async def member_count(self, ctx):
        string = f"```py\n{len([member for member in ctx.guild.members if not member.bot])}```"
        await ctx.send(string)

    @staticmethod
    def __community_report(guild):
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

    @staticmethod
    def df_match(c1, c2):
        if c1 == c2:
            return np.nan
        else:
            return c1

    @commands.command(name='user_activity()', help='See some stats on top users')
    async def user_activity(self, ctx):
        # path + activity.png
        file = discord.File(os.path.join(bot_config.path, 'activity.png'), filename='activity.png')
        await ctx.send(file=file)

    async def user_metrics_background_task(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(bot_config.guild_id)

        while not self.bot.is_closed():
            try:
                print('Updating user metrics...')
                online, idle, offline = self.__community_report(guild)
                with open(f"{bot_config.path}/usermetrics.csv", "a") as f:
                    f.write(f"{int(time.time())},{online},{idle},{offline}\n")
                    print(f"{int(time.time())},{online},{idle},{offline}")

                df_msgs = pd.read_csv(f'{bot_config.path}/msgs.csv', names=['time', 'uid', 'channel'])
                df_msgs = df_msgs[(df_msgs['time'] > time.time() - (86400 * bot_config.days_to_keep))]
                df_msgs['count'] = 1
                df_msgs['date'] = pd.to_datetime(df_msgs['time'], unit='s')
                df_msgs.drop(labels="time", axis=1, inplace=True)
                df_msgs.set_index("date", inplace=True)

                df_no_dup = df_msgs.copy()
                df_no_dup['uid2'] = df_no_dup['uid'].shift(-1)
                df_no_dup['uid_rm_dups'] = list(map(self.df_match, df_no_dup['uid'], df_no_dup['uid2']))

                df_no_dup.dropna(inplace=True)

                message_volume = df_msgs["count"].resample(bot_config.resample_interval).sum()

                user_id_counts_overall = Counter(
                    df_no_dup[
                        df_no_dup['channel'].isin([channel.id for channel in get_all_channels_by_tag('community')])][
                        'uid'].values).most_common(
                    bot_config.top_user_count)
                # print(user_id_counts_overall)

                uids_in_help = Counter(
                    df_no_dup[df_no_dup['channel'].isin([channel.id for channel in get_all_channels_by_tag('help')])][
                        'uid'].values).most_common(
                    bot_config.top_user_count)
                # print(uids_in_help)

                df = pd.read_csv(f"{bot_config.path}/usermetrics.csv", names=['time', 'online', 'idle', 'offline'])
                df = df[(df['time'] > time.time() - (86400 * bot_config.days_to_keep))]
                df['date'] = pd.to_datetime(df['time'], unit='s')
                df['total'] = df['online'] + df['offline'] + df['idle']
                df.drop(labels="time", axis=1, inplace=True)
                df.set_index("date", inplace=True)

                df = df.resample(bot_config.resample_interval).mean()
                df = df.join(message_volume)

                df.dropna(inplace=True)
                # print(df.head())
                DISCORD_BG_COLOR = '#36393E'

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
                plt.savefig(f"{bot_config.path}/online.png", facecolor=fig.get_facecolor())
                plt.clf()

                fig = plt.figure(facecolor=DISCORD_BG_COLOR)
                ax1 = plt.subplot2grid((2, 1), (0, 0))

                plt.xlabel("Message Volume")
                plt.title(f"General User Activity (past {bot_config.days_to_keep} days)")
                ax1.set_facecolor(DISCORD_BG_COLOR)

                users = []
                msgs = []
                for pair in user_id_counts_overall[::-1]:
                    try:
                        users.append(guild.get_member(pair[0]).name)  # get member name from here
                        if "Dhanos" in guild.get_member(pair[0]).name:
                            msgs.append(pair[1] / 1.0)
                        else:
                            msgs.append(pair[1])
                    except Exception as e:
                        print(str(e))
                y_pos = np.arange(len(users))
                ax1.barh(y_pos, msgs, align='center', alpha=0.5)
                plt.yticks(y_pos, users)

                ax2 = plt.subplot2grid((2, 1), (1, 0))
                plt.title(f"Help Channel Activity (past {bot_config.days_to_keep} days)")
                plt.xlabel("Help Channel\nMsg Volume")
                ax2.set_facecolor(DISCORD_BG_COLOR)

                users = []
                msgs = []
                for pair in uids_in_help[::-1]:
                    try:
                        users.append(guild.get_member(pair[0]).name)  # get member name from here

                        if "Dhanos" in guild.get_member(pair[0]).name:
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
                plt.savefig(f"{bot_config.path}/activity.png", facecolor=fig.get_facecolor())
                plt.clf()
                await asyncio.sleep(300)

            except FileNotFoundError as e:
                # create file if it doesn't exist
                print(str(e))
                if not os.path.exists(f"{bot_config.path}/usermetrics.csv"):
                    with open(f"{bot_config.path}/usermetrics.csv", "w") as f:
                        f.write("")
                # if msgs don't exist, create them
                if not os.path.exists(f"{bot_config.path}/msgs.csv"):
                    with open(f"{bot_config.path}/msgs.csv", "w") as f:
                        f.write("")
                if not os.path.exists(f"{bot_config.path}/logs.csv"):
                    with open(f"{bot_config.path}/logs.csv", "w") as f:
                        f.write("")
            except Exception as e:
                raise e



def setup(bot):
    bot.add_cog(CommunityStats(bot))
