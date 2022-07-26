import datetime
import disnake
from disnake.ext import commands, tasks
from typing import Optional

from util.logger import setup_custom_logger
from config import config
from database import messages_repo, audit_log_repo, users_repo, help_threads_repo, user_metrics_repo, guilds_repo
from features.base_cog import Base_Cog

logger = setup_custom_logger(__name__)

class Auditlog(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Auditlog, self).__init__(bot, __file__)

    if not self.cleanup_taks.is_running():
      self.cleanup_taks.start()

    if self.bot.is_ready():
      if not self.user_stats_task.is_running():
        self.user_stats_task.start()

  @commands.Cog.listener()
  async def on_ready(self):
    if not self.user_stats_task.is_running():
      self.user_stats_task.start()

  def cog_unload(self) -> None:
    if self.cleanup_taks.is_running():
      self.cleanup_taks.cancel()

    if self.user_stats_task.is_running():
      self.user_stats_task.cancel()

  def __del__(self):
    if self.cleanup_taks.is_running():
      self.cleanup_taks.cancel()

    if self.user_stats_task.is_running():
      self.user_stats_task.cancel()

  @tasks.loop(minutes=5)
  async def user_stats_task(self):
    guilds = self.bot.guilds
    for guild in guilds:
      user_metrics_repo.add_user_metrics(guild)
    user_metrics_repo.session.commit()

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.guild is None: return
    if message.author.bot: return
    if message.content.startswith(config.base.command_prefix): return

    thread = None
    channel = message.channel
    if isinstance(channel, disnake.Thread):
      thread = channel
      channel = channel.parent

    thread_id = thread.id if thread is not None else None
    if thread is not None:
      if help_threads_repo.thread_exists(thread_id):
        help_threads_repo.update_thread_activity(thread_id, datetime.datetime.utcnow(), commit=False)

    use_for_metrics = messages_repo.get_author_of_last_message_metric(channel.id, thread_id) != message.author.id
    messages_repo.add_message(message, use_for_metrics, commit=True)

  async def handle_message_edited(self, before: Optional[disnake.Message], after: disnake.Message):
    if after.guild is None: return
    if after.author.bot: return
    if after.content.startswith(config.base.command_prefix): return

    message_item = messages_repo.get_message(after.id)
    if before is None:
      before = message_item

    after_attachments = [att.url for att in after.attachments]

    if before is not None:
      if before.content == after.content and [att.url for att in before.attachments] == after_attachments:
        return

    await audit_log_repo.create_message_edited_log(self.bot, before, after)

    message_item.edited_at = after.edited_at
    message_item.content = after.content
    messages_repo.update_attachments(message_item, after.attachments)

  @commands.Cog.listener()
  async def on_message_delete(self, message: disnake.Message):
    if message.guild is None: return
    if message.author.bot: return
    if message.content.startswith(config.base.command_prefix): return

    messages_repo.delete_message(message.id, commit=False)
    audit_log_repo.create_message_deleted_log(message)

  @commands.Cog.listener()
  async def on_member_update(self, before: disnake.Member, after: disnake.Member):
    user_it = users_repo.get_member(after.id, after.guild.id)
    if user_it is not None:
      user_it.nick = after.display_name
      user_it.icon_url = after.display_avatar.url
      user_it.premium = after.premium_since is not None

    audit_log_repo.create_member_changed_log(before, after, commit=True)

  @commands.Cog.listener()
  async def on_member_join(self, member: disnake.Member):
    users_repo.get_or_create_member_if_not_exist(member)

  @commands.Cog.listener()
  async def on_member_remove(self, member: disnake.Member):
    users_repo.set_member_left(member)

  @commands.Cog.listener()
  async def on_guild_join(self, guild: disnake.Guild):
    guilds_repo.get_or_create_guild_if_not_exist(guild)
    for member in guild.members:
      users_repo.get_or_create_member_if_not_exist(member)

  @commands.Cog.listener()
  async def on_guild_remove(self, guild: disnake.Guild):
    guilds_repo.remove_guild(guild.id)

  @tasks.loop(hours=24)
  async def cleanup_taks(self):
    logger.info("Starting cleanup")
    if config.essentials.delete_left_users_after_days > 0:
      users_repo.delete_left_members(config.essentials.delete_left_users_after_days, commit=False)
    if config.essentials.delete_audit_logs_after_days > 0:
      audit_log_repo.delete_old_logs(config.essentials.delete_audit_logs_after_days, commit=False)
    if config.essentials.delete_messages_after_days > 0:
      messages_repo.delete_old_messages(config.essentials.delete_messages_after_days, commit=False)

    user_iterator = users_repo.get_all_users_iterator()
    for user_it in user_iterator:
      if len(user_it.members) == 0:
        users_repo.session.delete(user_it)

    users_repo.session.commit()
    logger.info("Cleanup finished")

def setup(bot):
  bot.add_cog(Auditlog(bot))
