from sqlalchemy import Column, String, DateTime
import datetime

from database import database

class HelpThread(database.base):
  __tablename__ = "help_threads"

  owner_id = Column(String, index=True)
  thread_id = Column(String, primary_key=True, unique=True, index=True)
  tags = Column(String, nullable=True)
  last_activity_time = Column(DateTime, index=True, default=datetime.datetime.utcnow)
