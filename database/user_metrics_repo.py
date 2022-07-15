from database import session
from database.tables.user_metrics import UserMetrics
import datetime
from typing import List

def add_user_metrics(online: int, idle: int, offline: int) -> UserMetrics:
  item = UserMetrics(timestamp=datetime.datetime.utcnow(), online=online, idle=idle, offline=offline)
  session.add(item)
  session.commit()
  return item

def get_user_metrics(days_back: int) -> List[UserMetrics]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  return session.query(UserMetrics).filter(UserMetrics.timestamp > threshold_date).order_by(UserMetrics.timestamp).all()
