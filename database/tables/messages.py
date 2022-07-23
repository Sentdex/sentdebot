from sqlalchemy import Column, DateTime, String, ForeignKey, Boolean

from database import database

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
