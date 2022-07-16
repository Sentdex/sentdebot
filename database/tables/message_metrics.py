from sqlalchemy import Column, DateTime, String

from database import database

class MessageMetrics(database.base):
  __tablename__ = "message_metrics"

  message_id = Column(String, primary_key=True, unique=True, index=True)
  timestamp = Column(DateTime, index=True)
  author_id = Column(String, index=True)
  channel_id = Column(String, index=True)
