from sqlalchemy import Column, String

from database import database

class Project(database.base):
  __tablename__ = "projects"

  name = Column(String, primary_key=True, unique=True, index=True)
  description = Column(String)
