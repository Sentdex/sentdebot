from sqlalchemy import Column, DateTime, String

from database import database

class User(database.base):
  __tablename__ = "users"

  id = Column(String, primary_key=True, unique=True, index=True)

  nick = Column(String, nullable=False, index=True)
  icon_url = Column(String, nullable=True)

  created_at = Column(DateTime, nullable=False)
  joined_at = Column(DateTime)
  left_at = Column(DateTime)
