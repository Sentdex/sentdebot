import disnake
import datetime
from typing import List, Tuple

from database import session
from database.tables.user_metrics import UserMetrics
from database import guilds_repo

def add_user_metrics(guild: disnake.Guild, commit: bool=True) -> UserMetrics:
  guilds_repo.get_or_create_guild_if_not_exist(guild)

  item = UserMetrics.from_guild(guild)
  session.add(item)
  if commit:
    session.commit()
  return item

def get_user_metrics(guild_id: int, days_back: int) -> List[Tuple[datetime.datetime, int, int, int]]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  data:List[UserMetrics] = session.query(UserMetrics).filter(UserMetrics.timestamp > threshold_date, UserMetrics.guild_id == str(guild_id)).order_by(UserMetrics.timestamp.desc()).all()

  output = []
  for d in data:
    output.append((d.timestamp, d.online, d.offline - d.online, d.offline))
  return output
