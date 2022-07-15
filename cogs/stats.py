import disnake
from disnake.ext import commands, tasks

from config import config
from features.base_cog import Base_Cog
from database import user_metrics_repo

class Stats(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Stats, self).__init__(bot, __file__)

    self.main_guild = None
    if self.bot.is_ready():
      self.late_init()

  def late_init(self):
    self.main_guild = self.bot.get_guild(config.main_guild_id) if config.main_guild_id != -1 or config.main_guild_id is not None else None
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

def setup(bot):
  bot.add_cog(Stats(bot))
