from sqlalchemy import Column, String

from database import database

class HelpThread(database.base):
  __tablename__ = "help_threads"

  owner_id = Column(String, index=True)
  message_id = Column(String, primary_key=True, unique=True, index=True)
