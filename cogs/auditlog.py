import datetime
import disnake
from disnake.ext import commands, tasks
from typing import Optional

from util import general_util
from util.logger import setup_custom_logger
from config import config
from database import messages_repo, audit_log_repo, users_repo, help_threads_repo, user_metrics_repo
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
    main_guild = self.bot.get_guild(config.ids.main_guild)
    if main_guild is not None:
      online, idle, offline = general_util.get_user_stats(main_guild)
      user_metrics_repo.add_user_metrics(online, idle, offline)

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

    users_repo.create_user_if_not_exist(message.author)
    use_for_metrics = messages_repo.get_author_of_last_message_metric(channel.id, thread_id) != message.author.id
    messages_repo.add_message(message.id, message.author.id, message.created_at, channel.id, thread.id if thread is not None else None, message.content, ";".join([att.url for att in message.attachments]), use_for_metrics, commit=True)

  async def handle_message_edited(self, before: Optional[disnake.Message], after: disnake.Message):
    if after.guild is None:
      return

    if after.guild.id != config.ids.main_guild:
      return

    message_item = messages_repo.get_message(after.id)
    if before is None:
      before = message_item

    after_attachments = ";".join([att.url for att in after.attachments])

    if before is not None:
      if isinstance(before, disnake.Message):
        if before.content == after.content and \
          ";".join([att.url for att in before.attachments]) == after_attachments:
          return
      else:
        if before.content == after.content and before.attachments == after.attachments:
          return

    audit_log_repo.create_message_edited_log(before, after)

    message_item.edited_at = after.edited_at
    message_item.content = after.content
    message_item.attachments = after_attachments

    messages_repo.session.commit()

  @commands.Cog.listener()
  async def on_message_delete(self, message: disnake.Message):
    if message.guild is None:
      return

    if message.guild.id != config.ids.main_guild:
      return

    audit_log_repo.create_message_deleted_log(message)

  @commands.Cog.listener()
  async def on_member_update(self, before: disnake.Member, after: disnake.Member):
    if after.guild.id != config.ids.main_guild:
      return

    user_it = users_repo.get_user(after.id)
    if user_it is not None:
      user_it.nick = after.display_name
      user_it.icon_url = after.display_avatar.url

    audit_log_repo.create_member_changed_log(before, after, commit=False)
    users_repo.session.commit()

  @commands.Cog.listener()
  async def on_member_join(self, member: disnake.Member):
    if member.guild.id != config.ids.main_guild:
      return

    users_repo.create_user_if_not_exist(member)

  @commands.Cog.listener()
  async def on_member_remove(self, member: disnake.Member):
    if member.guild.id != config.ids.main_guild:
      return

    user_it = users_repo.get_user(member.id)
    user_it.left_at = datetime.datetime.utcnow()
    users_repo.session.commit()

  @tasks.loop(hours=24)
  async def cleanup_taks(self):
    logger.info("Starting cleanup")
    if config.essentials.delete_left_users_after_days > 0:
      users_repo.delete_left_users(config.essentials.delete_left_users_after_days)
    if config.essentials.delete_audit_logs_after_days > 0:
      audit_log_repo.delete_old_logs(config.essentials.delete_audit_logs_after_days)
    if config.essentials.delete_messages_after_days > 0:
      messages_repo.delete_old_messages(config.essentials.delete_messages_after_days)
    logger.info("Cleanup finished")

def setup(bot):
  bot.add_cog(Auditlog(bot))
