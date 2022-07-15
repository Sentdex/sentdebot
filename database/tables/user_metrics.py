from sqlalchemy import Column, DateTime

from database import database, BigIntegerType

class UserMetrics(database.base):
  __tablename__ = "user_metrics"

  id = Column(BigIntegerType, primary_key=True, unique=True, index=True, autoincrement=True)

  timestamp = Column(DateTime, index=True)
  online = Column(BigIntegerType)
  idle = Column(BigIntegerType)
  offline = Column(BigIntegerType)
