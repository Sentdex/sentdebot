import datetime
import disnake
from disnake.ext import commands
from typing import Optional

from config import config
from database import messages_repo, audit_log_repo, users_repo
from features.base_cog import Base_Cog

class Auditlog(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Auditlog, self).__init__(bot, __file__)

  async def handle_message_edited(self, before: Optional[disnake.Message], after: disnake.Message):
    if after.guild is None:
      return

    if after.guild.id != config.ids.main_guild:
      return

    message_item = messages_repo.get_message(after.id)
    if before is None:
      before = message_item

    audit_log_repo.create_message_edited_log(before, after)

    message_item.edited_at = after.edited_at
    message_item.content = after.content
    message_item.attachments = ";".join([att.url for att in after.attachments])

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
      user_it.nick = after.nick
      user_it.icon_url = after.display_avatar

    audit_log_repo.create_member_changed_log(before, after, commit=False)
    users_repo.session.commit()

  @commands.Cog.listener()
  async def on_member_remove(self, member: disnake.Member):
    if member.guild.id != config.ids.main_guild:
      return

    user_it = users_repo.get_user(member.id)
    user_it.left_at = datetime.datetime.utcnow()
    users_repo.session.commit()

def setup(bot):
  bot.add_cog(Auditlog(bot))
