from sqlalchemy import Column, DateTime, String, Boolean

from database import database

class Message(database.base):
  __tablename__ = "messages"

  message_id = Column(String, primary_key=True, unique=True)
  timestamp = Column(DateTime, index=True)
  author_id = Column(String)
  channel_id = Column(String)
  content = Column(String)
  use_for_metric = Column(Boolean, index=True)
