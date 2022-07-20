from sqlalchemy import Column, DateTime, String

from database import database, BigIntegerType

class MessageMetric(database.base):
  __tablename__ = "message_metrics"

  message_id = Column(String, primary_key=True, unique=True)
  timestamp = Column(DateTime, index=True)
  author_id = Column(String)
  channel_id = Column(String)

class MessageContent(database.base):
  __tablename__ = "message_contents"

  id = Column(BigIntegerType, primary_key=True, unique=True, autoincrement=True)

  channel_id = Column(String, index=True)
  content = Column(String)
