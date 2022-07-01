"""Cog for calculating and displaying community stats"""
import os
import re
import time
from collections import Counter

import nextcord
from nextcord.ext import commands, tasks

import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from bot_config_manager import ReadOnlyConfig

config = ReadOnlyConfig()


class CommunityStats(commands.Cog):
    def __init__(self, bot):
        self.guild = bot.get_guild(config.get('guild_id'))
        self.COMMUNITY_BASED_CHANNELS = ["__main__",
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
                                         "show_and_tell", "politics_enter_at_own_risk"]

        self.HELP_CHANNELS = ["help",
                              "hello_technical_questions",
                              "help_0",
                              "help_1",
                              "help_2",
                              "help_3",
                              "help_overflow"]

        self.nextcord_BG_COLOR = '#36393E'
        self.MOST_COMMON_INT = 10
        self.bot = bot
        self.path = "./data/"
        # if path not exist, create
        os.makedirs(self.path, exist_ok=True)
        self.DAYS_BACK = 21
        self.RESAMPLE = '30min'

        self.draw_graphs.start()

    @commands.command(name='member_count()', help='get the member count')
    async def member_count(self, ctx):
        string = f"```py\n{len([member for member in ctx.guild.members if not member.bot])}```"
        await ctx.send(string)

    @commands.command(name='community_report()', help='get some stats on community')
    async def community_report(self, ctx):
        online, idle, offline = self.activity(ctx.guild)

        file = nextcord.File(f"{self.path}/online.png", filename=f"{self.path}/online.png")
        await ctx.send("", file=file)
        await ctx.send(
            f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    @staticmethod
    def activity(guild):
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
        await ctx.send(file=nextcord.File(os.path.join(self.path, 'activity.png'), filename='activity.png'))

    @tasks.loop(hours=1)  # because really, do we need to redraw this every 300s given the timescales?
    async def draw_graphs(self):
        msgs_file = os.path.join(self.path, "msgs.csv")
        # if msgs file not exist, create
        if not os.path.exists(msgs_file):
            with open(msgs_file, 'w') as f:
                f.write("")
        df_msgs = pd.read_csv(msgs_file, names=['time', 'uid', 'channel'])

        df_msgs = df_msgs[(df_msgs['time'] > time.time() - (86400 * self.DAYS_BACK))]
        df_msgs['count'] = 1
        df_msgs['date'] = pd.to_datetime(df_msgs['time'], unit='s')
        df_msgs.drop(labels="time", axis=1, inplace=True)
        df_msgs.set_index("date", inplace=True)

        df_no_dup = df_msgs.copy()
        df_no_dup['uid2'] = df_no_dup['uid'].shift(-1)
        df_no_dup['uid_rm_dups'] = list(map(self.df_match, df_no_dup['uid'], df_no_dup['uid2']))

        df_no_dup.dropna(inplace=True)

        message_volume = df_msgs["count"].resample(self.RESAMPLE).sum()

        user_id_counts_overall = Counter(
            df_no_dup[df_no_dup['channel'].isin(self.COMMUNITY_BASED_CHANNELS)]['uid'].values).most_common(
            self.MOST_COMMON_INT)

        uids_in_help = Counter(df_no_dup[df_no_dup['channel'].isin(self.HELP_CHANNELS)]['uid'].values).most_common(
            self.MOST_COMMON_INT)
        usermetrics_path = os.path.join(self.path, "usermetrics.csv")
        # if usermetrics file not exist, create
        if not os.path.exists(usermetrics_path):
            with open(usermetrics_path, 'w') as f:
                f.write("")
        df = pd.read_csv(usermetrics_path, names=['time', 'online', 'idle', 'offline'])
        df = df[(df['time'] > time.time() - (86400 * self.DAYS_BACK))]
        df['date'] = pd.to_datetime(df['time'], unit='s')
        df['total'] = df['online'] + df['offline'] + df['idle']
        df.drop(labels="time", axis=1, inplace=True)
        df.set_index("date", inplace=True)

        df = df.resample(self.RESAMPLE).mean()
        df = df.join(message_volume)

        df.dropna(inplace=True)

        fig = plt.figure(facecolor=self.nextcord_BG_COLOR)
        ax1 = plt.subplot2grid((2, 1), (0, 0))
        plt.ylabel("Active Users")
        plt.title("Community Report")
        ax1.set_facecolor(self.nextcord_BG_COLOR)
        ax1v = ax1.twinx()
        plt.ylabel("Message Volume")
        # ax1v.set_facecolor(self.nextcord_BG_COLOR)
        ax2 = plt.subplot2grid((2, 1), (1, 0))
        plt.ylabel("Total Users")
        ax2.set_facecolor(self.nextcord_BG_COLOR)

        ax1.plot(df.index, df.online, label="Active Users\n(Not Idle)")
        # ax1v.bar(df.index, df["count"], width=0.01)

        ax1v.fill_between(df.index, 0, df["count"], facecolor="w", alpha=0.2, label="Message Volume")
        ax1.legend(loc=2)
        ax1v.legend(loc=9)

        ax2.plot(df.index, df.total, label="Total Users")
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))

        ax2.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='lower'))
        ax2.legend()

        plt.subplots_adjust(left=0.11, bottom=0.10, right=0.89, top=0.95, wspace=0.2, hspace=0)
        ax1.get_xaxis().set_visible(False)

        ax1v.set_ylim(0, 3 * df["count"].values.max())

        plt.savefig(os.path.join(self.path, "online.png"), facecolor=fig.get_facecolor())
        plt.clf()

        fig = plt.figure(facecolor=self.nextcord_BG_COLOR)
        ax1 = plt.subplot2grid((2, 1), (0, 0))

        plt.xlabel("Message Volume")
        plt.title(f"General User Activity (past {self.DAYS_BACK} days)")
        ax1.set_facecolor(self.nextcord_BG_COLOR)

        users = []
        msgs = []
        for pair in user_id_counts_overall[::-1]:
            users.append(self.guild.get_member(pair[0]).name)  # get member name from here
            msgs.append(pair[1])

        y_pos = np.arange(len(users))
        ax1.barh(y_pos, msgs, align='center', alpha=0.5)
        plt.yticks(y_pos, users)

        ax2 = plt.subplot2grid((2, 1), (1, 0))
        plt.title(f"Help Channel Activity (past {self.DAYS_BACK} days)")
        plt.xlabel("Help Channel\nMsg Volume")
        ax2.set_facecolor(self.nextcord_BG_COLOR)

        users = []
        msgs = []
        for pair in uids_in_help[::-1]:
            name = self.guild.get_member(pair[0]).name
            # strip any glyphs from the name that doesn't exist in the font
            name = re.sub(r'[^\x00-\x7F]+', '', name)
            users.append(name)

            msgs.append(pair[1])
            # users.append(pair[0])

        y_pos = np.arange(len(users))
        ax2.barh(y_pos, msgs, align='center', alpha=0.5)
        plt.yticks(y_pos, users)

        plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)
        plt.savefig(os.path.join(self.path, "activity.png"), facecolor=fig.get_facecolor())
        plt.clf()
        plt.close()

    @tasks.loop(seconds=300)
    async def save_metrics(self):
        with open(os.path.join(self.path, "usermetrics.csv"), "a") as f:
            f.write("{},{},{},{}\n".format(int(time.time()), *self.activity(self.guild)))

    @draw_graphs.before_loop
    @save_metrics.before_loop
    async def metric_setup(self):
        await self.bot.wait_until_ready()
        if not self.guild:
            self.guild = self.bot.get_guild(self.guild_id)


def setup(bot):
    bot.add_cog(CommunityStats(bot))
