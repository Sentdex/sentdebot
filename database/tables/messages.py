import disnake
from disnake.ext import commands
from typing import Optional
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean

from database import database
from util import general_util

class Message(database.base):
  __tablename__ = "messages"

  message_id = Column(String, primary_key=True, unique=True)
  author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"))

  created_at = Column(DateTime, index=True, nullable=False)
  edited_at = Column(DateTime)

  channel_id = Column(String, index=True, nullable=False)
  thread_id = Column(String)
  content = Column(String)
  attachments = Column(String)

  use_for_metrics = Column(Boolean, nullable=False)

  async def to_object(self, bot: commands.Bot) -> Optional[disnake.Message]:
    message = await general_util.get_or_fetch_message(bot, None, int(self.message_id))
    if message is None:
      channel = await general_util.get_or_fetch_channel(bot, int(self.channel_id) if self.thread_id is None else int(self.thread_id))
      if channel is None: return None

      message = await general_util.get_or_fetch_message(bot, channel, int(self.message_id))

    return message
