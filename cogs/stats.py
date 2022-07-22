# Collect and show stats of main guild

import datetime
import disnake
from disnake.ext import commands, tasks
from typing import Optional, List, Tuple
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
from matplotlib import style
from matplotlib.font_manager import FontProperties
import io

style.use("dark_background")
font_prop = FontProperties()
font_prop.set_file("static_data/STIXTwoText-Bold.ttf")
plt.rcParams["font.family"] = font_prop.get_family()

style.use("dark_background")

from config import cooldowns
from util import general_util
from config import config
from features.base_cog import Base_Cog
from database import user_metrics_repo, messages_repo, help_threads_repo
from static_data.strings import Strings
from util.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

def df_match(c1, c2):
  if c1 == c2:
    return np.nan
  else:
    return c1

class Stats(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Stats, self).__init__(bot, __file__)

    if self.bot.is_ready():
      self.late_init()

    self.user_activity_image: Optional[Tuple[io.BytesIO, datetime.datetime]] = None
    self.community_report_image: Optional[Tuple[io.BytesIO, datetime.datetime]] = None

  def late_init(self):
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

  def get_user_stats(self, guild):
    members = guild.members

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
    main_guild = self.bot.get_guild(config.ids.main_guild)
    if main_guild is not None:
      online, idle, offline = self.get_user_stats(main_guild)
      user_metrics_repo.add_user_metrics(online, idle, offline)
    else:
      self.late_init()

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    main_guild = self.bot.get_guild(config.ids.main_guild)

    if main_guild is None: return
    if message.guild is None: return
    if main_guild.id != message.guild.id: return
    if message.author.bot: return
    if message.content == "" or message.content.startswith(config.base.command_prefix + "."): return

    thread = None
    channel = message.channel
    if isinstance(channel, disnake.Thread):
      thread = channel
      channel = channel.parent

    thread_id = thread.id if thread is not None else None
    if thread is not None:
      if help_threads_repo.thread_exists(thread_id):
        help_threads_repo.update_thread_activity(thread_id, message.created_at, commit=False)

    if messages_repo.get_author_of_last_message_metric(channel.id, thread_id) != message.author.id:
      messages_repo.add_message_metric(message.id, channel.id, thread_id, message.author.id, commit=False)

    messages_repo.add_message_content(channel.id, thread_id, message.content)

  async def handle_message_edited(self, _, after: disnake.Message):
    message_item = messages_repo.get_message_metric(after.id)
    if message_item is not None:
      message_item.content = after.content
      messages_repo.session.commit()

  @commands.command(brief=Strings.stats_stats_brief)
  @cooldowns.default_cooldown
  async def stats(self, ctx: commands.Context):
    await self.user_activity(ctx)
    await self.community_report(ctx)

  @commands.command(brief=Strings.stats_user_activity_brief)
  @cooldowns.default_cooldown
  async def user_activity(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)
    main_guild = self.bot.get_guild(config.ids.main_guild)

    if main_guild is None:
      return general_util.generate_error_message(ctx, Strings.stats_main_guild_not_set)

    if self.user_activity_image is not None and datetime.datetime.utcnow() - self.user_activity_image[1] < datetime.timedelta(minutes=config.stats.max_graph_minutes_age_for_regenerate):
      logger.info("Taking user activity from cache")

      self.user_activity_image[0].seek(0)
      embed = disnake.Embed(title="User activity", color=disnake.Color.dark_blue())
      general_util.add_author_footer(embed, ctx.author)
      embed.set_image(file=disnake.File(self.user_activity_image[0], "user_activity.png"))
      return await ctx.send(embed=embed)

    logger.info("Generating new user activity")
    all_channels = [channel.id for channel in main_guild.channels]

    message_history = messages_repo.get_message_metrics(config.stats.days_back)
    dataframe = pd.DataFrame.from_records(message_history, columns=["message_id", "timestamp", "author_id", "channel_id"])
    dataframe["date"] = pd.to_datetime(dataframe["timestamp"], unit="s")
    dataframe.set_index("date", inplace=True)
    dataframe.drop("timestamp", axis=1, inplace=True)

    user_id_counts_overall = Counter(dataframe[dataframe["channel_id"].isin(all_channels)]["author_id"].values).most_common(10)
    uids_in_help = Counter(dataframe[dataframe["channel_id"].isin([config.ids.help_channel])]["author_id"].values).most_common(10)

    fig = plt.figure(facecolor=config.stats.graph_bg_color_code)
    fig.set_dpi(200)

    ax1 = plt.subplot2grid((2, 1), (0, 0))

    plt.xlabel("Message Volume")
    plt.title(f"General User Activity (past {config.stats.days_back} days)")
    ax1.set_facecolor(config.stats.graph_bg_color_code)

    users = []
    msgs = []
    for pair in user_id_counts_overall[::-1]:
      member = main_guild.get_member(pair[0])
      if member is not None:
        users.append(general_util.truncate_string(member.name, limit=config.stats.name_length_limit))
        msgs.append(pair[1])

    y_pos = np.arange(len(users))
    ax1.barh(y_pos, msgs, align='center', alpha=0.5)
    plt.yticks(y_pos, users)

    ax2 = plt.subplot2grid((2, 1), (1, 0))
    plt.title(f"Help Channel Activity (past {config.stats.days_back} days)")
    plt.xlabel("Help Channel\nMsg Volume")
    ax2.set_facecolor(config.stats.graph_bg_color_code)

    users = []
    msgs = []
    for pair in uids_in_help[::-1]:
      member = main_guild.get_member(pair[0])
      if member is not None:
        users.append(general_util.truncate_string(member.name, limit=config.stats.name_length_limit))
        msgs.append(pair[1])

    y_pos = np.arange(len(users))
    ax2.barh(y_pos, msgs, align='center', alpha=0.5)
    plt.yticks(y_pos, users)

    plt.subplots_adjust(left=0.30, bottom=0.15, right=0.99, top=0.95, wspace=0.2, hspace=0.55)

    buf = io.BytesIO()
    plt.savefig(buf, facecolor=fig.get_facecolor(), format='png')
    buf.seek(0)
    plt.clf()

    self.user_activity_image = (buf, datetime.datetime.utcnow())

    embed = disnake.Embed(title="User activity", color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)
    embed.set_image(file=disnake.File(buf, "user_activity.png"))
    await ctx.send(embed=embed)

  @commands.command(brief=Strings.stats_community_report_brief)
  @cooldowns.default_cooldown
  async def community_report(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)
    main_guild = self.bot.get_guild(config.ids.main_guild)

    if main_guild is None:
      return general_util.generate_error_message(ctx, Strings.stats_main_guild_not_set)

    if self.community_report_image is not None and datetime.datetime.utcnow() - self.community_report_image[1] < datetime.timedelta(minutes=config.stats.max_graph_minutes_age_for_regenerate):
      logger.info("Taking community report from cache")

      self.community_report_image[0].seek(0)

      online, idle, offline = self.get_user_stats(main_guild)
      embed = disnake.Embed(title="Community report", description=f"Online: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}", color=disnake.Color.dark_blue())
      general_util.add_author_footer(embed, ctx.author)
      embed.set_image(file=disnake.File(self.community_report_image[0], "community_report.png"))
      return await ctx.send(embed=embed)

    logger.info("Generating new community report")

    message_history = messages_repo.get_message_metrics(config.stats.days_back)
    message_df = pd.DataFrame.from_records(
      message_history,
      columns=["message_id", "timestamp", "author_id", "channel_id"]
    )
    volume_df = (
      message_df
      .assign(date=lambda df: pd.to_datetime(df.timestamp, unit='s').dt.floor('H'))
      .groupby('date')
      .size()
    )

    users_metrics = user_metrics_repo.get_user_metrics(config.stats.days_back)
    users_metrics_df = pd.DataFrame.from_records(
      users_metrics,
      columns=["timestamp", "online", "idle", "offline"]
    )
    users_metrics_df = (
      users_metrics_df
      .assign(date=lambda df: pd.to_datetime(df.timestamp, unit='s').dt.floor('H'),
              total=lambda df: df.online + df.offline + df.idle)
      .drop(columns='timestamp')
      .groupby('date')
      .mean()
    )
    users_metrics_dataframe = pd.concat(
      [users_metrics_df, volume_df.rename('count')],
      axis=1
    ).fillna(0)

    fig = plt.figure(facecolor=config.stats.graph_bg_color_code)
    fig.set_dpi(200)

    ax1 = plt.subplot2grid((3, 1), (0, 0))
    plt.ylabel("Active Users")
    plt.title("Community Report")
    ax1.set_facecolor(config.stats.graph_bg_color_code)
    ax1v = ax1.twinx()
    plt.ylabel("Message Volume")

    ax2 = plt.subplot2grid((3, 1), (1, 0))
    plt.ylabel("Users")
    ax2.set_facecolor(config.stats.graph_bg_color_code)

    ax3 = plt.subplot2grid((3, 1), (2, 0))
    plt.ylabel("Total Users")
    ax3.set_facecolor(config.stats.graph_bg_color_code)

    ax1.plot(users_metrics_dataframe.index, users_metrics_dataframe.online, label="Active Users\n(Not Idle)")
    # ax1v.bar(df.index, df["count"], width=0.01)

    ax1v.fill_between(users_metrics_dataframe.index, 0, users_metrics_dataframe["count"], facecolor="w", alpha=0.2, label="Message Volume")
    ax1.legend(loc=2)
    ax1v.legend(loc=9)

    ax2.plot(users_metrics_dataframe.index, users_metrics_dataframe.online.rolling(3).mean(), label="Online Users")
    ax2.plot(users_metrics_dataframe.index, users_metrics_dataframe.idle.rolling(3).mean(), label="Idle Users")
    ax2.plot(users_metrics_dataframe.index, users_metrics_dataframe.offline.rolling(3).mean(), label="Offline Users")
    ax2.legend(loc=2)
    ax2.get_xaxis().set_visible(False)

    ax3.plot(users_metrics_dataframe.index, users_metrics_dataframe.total, label="Total Users")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M'))

    # for label in ax2.xaxis.get_ticklabels():
    #        label.set_rotation(45)
    ax3.xaxis.set_major_locator(mticker.MaxNLocator(nbins=5, prune='lower'))
    ax3.legend()

    plt.subplots_adjust(left=0.11, bottom=0.10, right=0.89, top=0.95, wspace=0.2, hspace=0)
    ax1.get_xaxis().set_visible(False)

    ax1v.set_ylim(0, 3 * users_metrics_dataframe["count"].values.max())

    buf = io.BytesIO()
    plt.savefig(buf, facecolor=fig.get_facecolor(), format='png')
    buf.seek(0)
    plt.clf()

    self.community_report_image = (buf, datetime.datetime.utcnow())

    online, idle, offline = self.get_user_stats(main_guild)
    embed = disnake.Embed(title="Community report", description=f"Online: {online}\nIdle/busy/dnd: {idle}\nOffline: {offline}", color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)
    embed.set_image(file=disnake.File(buf, "community_report.png"))
    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Stats(bot))
