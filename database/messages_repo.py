from database import session
from database.tables.messages import MessageMetric, MessageContent
import datetime
from typing import List, Tuple, Optional

def add_message_metric(message_id: int, channel_id: int, thread_id: Optional[int], author_id: int, commit: bool=True) -> MessageMetric:
  item = MessageMetric(message_id=str(message_id), timestamp=datetime.datetime.utcnow(), author_id=str(author_id), channel_id=str(channel_id), thread_id=str(thread_id) if thread_id is not None else None)
  session.add(item)
  if commit:
    session.commit()
  return item

def get_message_metric(message_id: int) -> Optional[MessageMetric]:
  return session.query(MessageMetric).filter(MessageMetric.message_id == str(message_id)).one_or_none()

def get_message_metrics(days_back: int) -> List[Tuple[int, datetime.datetime, int, int]]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  data = session.query(MessageMetric.message_id, MessageMetric.timestamp, MessageMetric.author_id, MessageMetric.channel_id).filter(MessageMetric.timestamp > threshold_date).order_by(MessageMetric.timestamp.desc()).all()
  return [(int(d[0]), d[1], int(d[2]), int(d[3])) for d in data]

def get_author_of_last_message_metric(channel_id: int, thread_id: Optional[int]) -> Optional[int]:
  user_id = session.query(MessageMetric.author_id).filter(MessageMetric.channel_id == str(channel_id), MessageMetric.thread_id == str(thread_id) if thread_id is not None else None).order_by(MessageMetric.timestamp.desc()).first()
  return int(user_id[0]) if user_id is not None else None

def add_message_content(channel_id: int, thread_id: Optional[int], content: str):
  item = MessageContent(channel_id=str(channel_id), thread_id=str(thread_id) if thread_id is not None else None, content=content)
  session.add(item)
  session.commit()
  return item
