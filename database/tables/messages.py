import disnake
from disnake.ext import commands
from typing import Optional
from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from database import database
from util import general_util

class MessageAttachment(database.base):
  __tablename__ = "message_attachments"

  id = Column(String, primary_key=True, unique=True)

  message_id = Column(String, ForeignKey("messages.id", ondelete="CASCADE"), index=True, nullable=False)
  url = Column(String, index=True, nullable=False)

  message = relationship("Message", back_populates="attachments")

class Message(database.base):
  __tablename__ = "messages"

  id = Column(String, primary_key=True, unique=True, index=True)
  author_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
  guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), nullable=True)

  created_at = Column(DateTime, index=True, nullable=False)
  edited_at = Column(DateTime)

  channel_id = Column(String, index=True, nullable=False)
  thread_id = Column(String)
  content = Column(String)

  attachments = relationship("MessageAttachment", back_populates="message", uselist=True)

  use_for_metrics = Column(Boolean, nullable=False, default=False)

  @classmethod
  def from_message(cls, message: disnake.Message):
    channel_is_thread = isinstance(message.channel, disnake.Thread)
    channel_id = message.channel.parent.id if channel_is_thread else message.channel.id
    thread_id = message.channel.id if channel_is_thread else None
    return cls(id=str(message.id), author_id=str(message.author.id), guild_id=str(message.guild.id) if message.guild is not None else None, created_at=message.created_at, channel_id=str(channel_id), thread_id=str(thread_id) if thread_id is not None else None, content=message.content)

  async def to_object(self, bot: commands.Bot) -> Optional[disnake.Message]:
    message = await general_util.get_or_fetch_message(bot, None, int(self.message_id))
    if message is None:
      channel = await general_util.get_or_fetch_channel(bot, int(self.channel_id) if self.thread_id is None else int(self.thread_id))
      if channel is None: return None

      message = await general_util.get_or_fetch_message(bot, channel, int(self.message_id))

    return message
