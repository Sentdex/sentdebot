from sqlalchemy import Column, DateTime, String, Enum, JSON, ForeignKey
import enum
import datetime

from database import database, BigIntegerType

class AuditLogItemType(enum.Enum):
  MESSAGE_DELETED = 0
  MESSAGE_EDITED = 1
  MEMBER_UPDATED = 2

class AuditLog(database.base):
  __tablename__ = "audit_log"

  id = Column(BigIntegerType, primary_key=True, index=True, autoincrement=True, unique=True)
  timestamp = Column(DateTime, index=True, nullable=False, default=datetime.datetime.utcnow)

  user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)
  guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"), index=True, nullable=True)

  log_type = Column(Enum(AuditLogItemType), index=True)
  data = Column(JSON, nullable=True)
