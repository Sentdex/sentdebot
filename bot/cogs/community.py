import logging
import time
import traceback
from collections import Counter

import discord
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
from bot import SentdeBot
from discord.ext import commands, tasks
from discord.ext.commands import Cog, command
from discord.ext.commands.context import Context
from discord.ext.commands.errors import CommandError

from .utils import community_report, in_channels


def df_match(c1, c2):
    if c1 == c2:
        return np.nan
    else:
        return c1

class Community(Cog):
    logger = logging.getLogger(f"<Cog 'Community' at {__name__}>")
    def __init__(self, bot) -> None:
        self.bot = bot
        # add attributes here so that we dont have to access bot repeatedly
        self.guild = None
        self.path = self.bot.path
        self.DAYS_BACK = self.bot.DAYS_BACK
        self.RESAMPLE = self.bot.RESAMPLE
        self.MOST_COMMON_INT = self.bot.MOST_COMMON_INT
        self.COMMUNITY_BASED_CHANNELS = self.bot.COMMUNITY_BASED_CHANNELS
        self.DISCORD_BG_COLOR = str(discord.Colour.dark_theme())

    @command()
    async def member_count(self, ctx: Context):
        await ctx.send(f"```py\n{ctx.bot.guild.member_count}```")

    @command()
    @in_channels(SentdeBot.image_channels)
    async def community_report(self, ctx: Context):
        online, idle, offline = community_report(self.guild)
        file = discord.File(self.path / "online.png", filename=f"online.png")
        await ctx.send("", file=file)
        await ctx.send(f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    @command()
    @in_channels(SentdeBot.image_channels)
    async def user_activity(self, ctx: Context):
        file = discord.File(self.bot.path / "activity.png", filename=f"activity.png")
        await ctx.send("", file=file)

    @community_report.error
    @user_activity.error
    async def error_handler(self, ctx: Context, error: CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f"Cannot use `{ctx.command.qualified_name}` in this channel!", delete_after=5.0)
        else:
            self.logger.error(f"In {ctx.command.qualified_name}:")
            traceback.print_tb(error.original.__traceback__)
            self.logger.error(
                f"{error.original.__class__.__name__}: {error.original}")


    # The try-catch blocks are removed because
    # the default error handler for a :class:`discord.ext.task.Loop`
    # prints to sys.sterr by default.
    # <https://discordpy.readthedocs.io/en/latest/ext/tasks/index.html#discord.ext.tasks.Loop.error>
    @tasks.loop(seconds=300)
    async def user_metrics(self):
        online, idle, offline = community_report(self.guild)
        # self.path: pathlib.Path
        with open(self.path / "usermetrics.csv", "a") as f:
            f.write(f"{int(time.time())},{online},{idle},{offline}\n")

        df_msgs = pd.read_csv(str(self.path / "msgs.csv"), names=['time', 'uid', 'channel'])
        df_msgs = df_msgs[(df_msgs['time'] > time.time()-(86400*self.DAYS_BACK))]
        df_msgs['count'] = 1
        df_msgs['date'] = pd.to_datetime(df_msgs['time'], unit='s')
        df_msgs.drop("time", 1,  inplace=True)
        df_msgs.set_index("date", inplace=True)


        df_no_dup = df_msgs.copy()
        df_no_dup['uid2'] = df_no_dup['uid'].shift(-1)
        df_no_dup['uid_rm_dups'] = list(map(df_match, df_no_dup['uid'], df_no_dup['uid2']))

        df_no_dup.dropna(inplace=True)


        message_volume = df_msgs["count"].resample(self.RESAMPLE).sum()

        user_id_counts_overall = Counter(df_no_dup[df_no_dup['channel'].isin(self.COMMUNITY_BASED_CHANNELS)]['uid'].values).most_common(self.MOST_COMMON_INT)
        #print(user_id_counts_overall)

        uids_in_help = Counter(df_no_dup[df_no_dup['channel'].isin(self.HELP_CHANNELS)]['uid'].values).most_common(self.MOST_COMMON_INT)
        #print(uids_in_help)

        df = pd.read_csv(str(self.path / "usermetrics.csv"), names=['time', 'online', 'idle', 'offline'])
        df = df[(df['time'] > time.time()-(86400*self.DAYS_BACK))]
        df['date'] = pd.to_datetime(df['time'],unit='s')
        df['total'] = df['online'] + df['offline'] + df['idle']
        df.drop("time", 1,  inplace=True)
        df.set_index("date", inplace=True)

        df = df.resample(self.RESAMPLE).mean()
        df = df.join(message_volume)

        df.dropna(inplace=True)
        #print(df.head())

        fig = plt.figure(facecolor=self.DISCORD_BG_COLOR)
        ax1 = plt.subplot2grid((2, 1), (0, 0))
        plt.ylabel("Active Users")
        plt.title("Community Report")
        ax1.set_facecolor(self.DISCORD_BG_COLOR)
        ax1v = ax1.twinx()
        plt.ylabel("Message Volume")
        #ax1v.set_facecolor(self.DISCORD_BG_COLOR)
        ax2 = plt.subplot2grid((2, 1), (1, 0))
        plt.ylabel("Total Users")
        ax2.set_facecolor(self.DISCORD_BG_COLOR)

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
        plt.savefig(f"{self.path}/online.png", facecolor = fig.get_facecolor())
        plt.clf()


        fig = plt.figure(facecolor=self.DISCORD_BG_COLOR)
        ax1 = plt.subplot2grid((2, 1), (0, 0))

        plt.xlabel("Message Volume")
        plt.title(f"General User Activity (past {self.DAYS_BACK} days)")
        ax1.set_facecolor(self.DISCORD_BG_COLOR)

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
        ax2.set_facecolor(self.DISCORD_BG_COLOR)

        users = []
        msgs = []
        for pair in uids_in_help[::-1]:
            users.append(self.guild.get_member(pair[0]).name)  # get member name from here
            msgs.append(pair[1])
            #users.append(pair[0])

        y_pos = np.arange(len(users))
        ax2.barh(y_pos, msgs, align='center', alpha=0.5)
        plt.yticks(y_pos, users)

        plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)
        plt.savefig(f"{self.path}/activity.png", facecolor=fig.get_facecolor())
        plt.clf()

    @user_metrics.before_loop
    async def metric_setup(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.guild

        if not self.guild:
            self.guild = self.bot.get_guild(self.bot.guild_id)

# Just incase we require more control over extensions in the future
def setup(bot):
    bot.add_cog(Community(bot))
