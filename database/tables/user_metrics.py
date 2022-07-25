import disnake
import datetime
from sqlalchemy import Column, DateTime, ForeignKey, String

from database import database, BigIntegerType
from util import general_util

class UserMetrics(database.base):
  __tablename__ = "user_metrics"

  id = Column(BigIntegerType, primary_key=True, unique=True, index=True, autoincrement=True)

  guild_id = Column(String, ForeignKey("guilds.id", ondelete="CASCADE"))
  timestamp = Column(DateTime, index=True)
  online = Column(BigIntegerType)
  offline = Column(BigIntegerType)

  @classmethod
  def from_guild(cls, guild: disnake.Guild):
    online, offline = general_util.get_user_stats(guild)
    return cls(guild_id=str(guild.id), timestamp=datetime.datetime.utcnow(), online=online, offline=offline)
