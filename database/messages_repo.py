from database import session
from database.tables.messages import Message
import datetime
from typing import List, Tuple, Optional
from sqlalchemy import and_

def add_message(message_id: int, channel_id: int, author_id: int, content: str, use_for_metrics: bool=False) -> Message:
  item = Message(message_id=str(message_id), timestamp=datetime.datetime.utcnow(), author_id=str(author_id), channel_id=str(channel_id), content=content, use_for_metric=use_for_metrics)
  session.add(item)
  session.commit()
  return item

def get_message_metrics(days_back: int) -> List[Tuple[int, datetime.datetime, int, int]]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  data:List[Message] = session.query(Message).filter(and_(Message.timestamp > threshold_date, Message.use_for_metric == True)).order_by(Message.timestamp.desc()).all()
  return [(int(d.message_id), d.timestamp, int(d.author_id), int(d.channel_id)) for d in data]

def get_author_of_last_message_metric(channel_id: int) -> Optional[int]:
  user_id = session.query(Message.author_id).filter(and_(Message.channel_id == str(channel_id), Message.use_for_metric == True)).order_by(Message.timestamp.desc()).first()
  return int(user_id[0]) if user_id is not None else None
