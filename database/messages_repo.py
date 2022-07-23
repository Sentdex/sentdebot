from database import session
from database.tables.messages import Message
import datetime
from typing import List, Tuple, Optional

def add_message(message_id: int, author_id: int, created_at: datetime.datetime, channel_id: int, thread_id: Optional[int], content: Optional[str], attachments: Optional[str], use_for_metrics: bool=True, commit: bool=True) -> Message:
  item = Message(message_id=str(message_id), author_id=str(author_id), created_at=created_at, channel_id=str(channel_id), thread_id=str(thread_id) if thread_id is not None else None, content=content, attachments=attachments, use_for_metrics=use_for_metrics)
  session.add(item)
  if commit:
    session.commit()
  return item

def get_message(message_id: int) -> Optional[Message]:
  return session.query(Message).filter(Message.message_id == str(message_id)).one_or_none()

def get_message_metrics(days_back: int) -> List[Tuple[int, datetime.datetime, int, int]]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  data = session.query(Message.message_id, Message.created_at, Message.author_id, Message.channel_id).filter(Message.created_at > threshold_date, Message.use_for_metrics == True).order_by(Message.created_at.desc()).all()
  return [(int(d[0]), d[1], int(d[2]), int(d[3])) for d in data]

def get_author_of_last_message_metric(channel_id: int, thread_id: Optional[int]) -> Optional[int]:
  user_id = session.query(Message.author_id).filter(Message.channel_id == str(channel_id), Message.thread_id == (str(thread_id) if thread_id is not None else None), Message.use_for_metrics == True).order_by(Message.created_at.desc()).first()
  return int(user_id[0]) if user_id is not None else None
