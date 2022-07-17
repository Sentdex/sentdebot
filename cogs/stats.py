# Collect and show stats of main guild

import disnake
from disnake.ext import commands, tasks
from typing import Optional, List
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib import style
import io

style.use("dark_background")

from config import cooldowns
from util import general_util
from config import config
from features.base_cog import Base_Cog
from database import user_metrics_repo, message_metrics_repo
from static_data.strings import Strings

DISCORD_BG_COLOR = '#36393E'

def df_match(c1, c2):
  if c1 == c2:
    return np.nan
  else:
    return c1

class Stats(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Stats, self).__init__(bot, __file__)

    self.all_channels: List[int] = []
    self.main_guild: Optional[disnake.Guild] = None
    if self.bot.is_ready():
      self.late_init()

  def late_init(self):
    self.main_guild = self.bot.get_guild(config.main_guild_id) if config.main_guild_id != -1 or config.main_guild_id is not None else None
    self.all_channels = [channel.id for channel in self.main_guild.channels] if self.main_guild is not None else []

    if not self.user_stats_task.is_running():
      self.user_stats_task.start()

  def cog_unload(self) -> None:
    if self.user_stats_task.is_running():
      self.user_stats_task.cancel()

  def __del__(self):
    if self.user_stats_task.is_running():
      self.user_stats_task.cancel()

  @commands.Cog.listener()
  async def on_ready(self):
    self.late_init()

  def get_user_stats(self):
    members = self.main_guild.members

    online, idle, offline = 0, 0, 0
    for member in members:
      if member.status == disnake.Status.online:
        online += 1
      elif member.status == disnake.Status.offline:
        offline += 1
      else:
        idle += 1

    return online, idle, offline

  @tasks.loop(minutes=5)
  async def user_stats_task(self):
    if self.main_guild is not None:
      online, idle, offline = self.get_user_stats()
      user_metrics_repo.add_user_metrics(online, idle, offline)
    else:
      self.late_init()

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if self.main_guild is None: return
    if self.main_guild.id != message.guild.id: return
    if message.author.bot: return
    if message.guild is None: return

    if message_metrics_repo.get_author_of_last_message(message.channel.id) != message.author.id:
      message_metrics_repo.add_message_metrics(message)

  @commands.command(brief=Strings.stats_user_activity_brief)
  @cooldowns.long_cooldown
  async def user_activity(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)

    if self.main_guild is None:
      return general_util.generate_error_message(ctx, Strings.stats_main_guild_not_set)

    message_history = message_metrics_repo.get_message_metrics(config.stats_days_back)
    dataframe = pd.DataFrame.from_records(message_history, columns=["message_id", "timestamp", "author_id", "channel_id"])
    dataframe["date"] = pd.to_datetime(dataframe["timestamp"], unit="s")
    dataframe.set_index("date", inplace=True)
    dataframe.drop("timestamp", axis=1, inplace=True)

    user_id_counts_overall = Counter(dataframe[dataframe["channel_id"].isin(self.all_channels)]["author_id"].values).most_common(10)
    uids_in_help = Counter(dataframe[dataframe["channel_id"].isin([config.base_help_channel_id])]["author_id"].values).most_common(10)

    fig = plt.figure(facecolor=DISCORD_BG_COLOR)
    ax1 = plt.subplot2grid((2, 1), (0, 0))

    plt.xlabel("Message Volume")
    plt.title(f"General User Activity (past {config.stats_days_back} days)")
    ax1.set_facecolor(DISCORD_BG_COLOR)

    users = []
    msgs = []
    for pair in user_id_counts_overall[::-1]:
      member = self.main_guild.get_member(pair[0])
      if member is not None:
        users.append(member.name)
        msgs.append(pair[1])

    y_pos = np.arange(len(users))
    ax1.barh(y_pos, msgs, align='center', alpha=0.5)
    plt.yticks(y_pos, users)

    ax2 = plt.subplot2grid((2, 1), (1, 0))
    plt.title(f"Help Channel Activity (past {config.stats_days_back} days)")
    plt.xlabel("Help Channel\nMsg Volume")
    ax2.set_facecolor(DISCORD_BG_COLOR)

    users = []
    msgs = []
    for pair in uids_in_help[::-1]:
      member = self.main_guild.get_member(pair[0])
      if member is not None:
        users.append(member.name)
        msgs.append(pair[1])

    y_pos = np.arange(len(users))
    ax2.barh(y_pos, msgs, align='center', alpha=0.5)
    plt.yticks(y_pos, users)

    plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)

    buf = io.BytesIO()
    plt.savefig(buf, facecolor=fig.get_facecolor(), format='png')
    buf.seek(0)
    plt.clf()

    embed = disnake.Embed(title="User activity", color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)
    embed.set_image(file=disnake.File(buf, "user_activity.png"))
    await ctx.send(embed=embed)

  @commands.command(brief=Strings.stats_community_report_brief)
  @cooldowns.long_cooldown
  async def community_report(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)

    if self.main_guild is None:
      return general_util.generate_error_message(ctx, Strings.stats_main_guild_not_set)

    message_history = message_metrics_repo.get_message_metrics(config.stats_days_back)
    message_dataframe = pd.DataFrame.from_records(message_history, columns=["message_id", "timestamp", "author_id", "channel_id"])
    message_dataframe['count'] = 1
    message_dataframe["date"] = pd.to_datetime(message_dataframe["timestamp"], unit="s")
    message_dataframe.set_index("date", inplace=True)
    message_dataframe.drop("timestamp", axis=1, inplace=True)

    message_volume = message_dataframe["count"].resample("60min").sum()

    users_metrics = user_metrics_repo.get_user_metrics(config.stats_days_back)
    users_metrics_dataframe = pd.DataFrame.from_records(users_metrics, columns=["timestamp", "online", "idle", "offline"])
    users_metrics_dataframe['date'] = pd.to_datetime(users_metrics_dataframe['timestamp'], unit='s')
    users_metrics_dataframe.set_index("date", inplace=True)
    users_metrics_dataframe.drop("timestamp", axis=1, inplace=True)
    users_metrics_dataframe['total'] = users_metrics_dataframe['online'] + users_metrics_dataframe['offline'] + users_metrics_dataframe['idle']

    users_metrics_dataframe = users_metrics_dataframe.resample("60min").mean()
    users_metrics_dataframe = users_metrics_dataframe.join(message_volume)

    users_metrics_dataframe.dropna(inplace=True)

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

    ax1.plot(users_metrics_dataframe.index, users_metrics_dataframe.online, label="Active Users\n(Not Idle)")
    # ax1v.bar(df.index, df["count"], width=0.01)

    ax1v.fill_between(users_metrics_dataframe.index, 0, users_metrics_dataframe["count"], facecolor="w", alpha=0.2, label="Message Volume")
    ax1.legend(loc=2)
    ax1v.legend(loc=9)

    ax2.plot(users_metrics_dataframe.index, users_metrics_dataframe.total, label="Total Users")
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))

    # for label in ax2.xaxis.get_ticklabels():
    #        label.set_rotation(45)
    ax2.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='lower'))
    ax2.legend()

    plt.subplots_adjust(left=0.11, bottom=0.10, right=0.89, top=0.95, wspace=0.2, hspace=0)
    ax1.get_xaxis().set_visible(False)

    ax1v.set_ylim(0, 3 * users_metrics_dataframe["count"].values.max())

    buf = io.BytesIO()
    plt.savefig(buf, facecolor=fig.get_facecolor(), format='png')
    buf.seek(0)
    plt.clf()

    online, idle, offline = self.get_user_stats()
    embed = disnake.Embed(title="Community report", description=f"Online: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}", color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)
    embed.set_image(file=disnake.File(buf, "community_report.png"))
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Stats(bot))
