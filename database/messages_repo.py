import disnake
import datetime
from typing import List, Tuple, Optional

from database import session
from database.tables.messages import Message
from database import users_repo


def add_message(message: disnake.Message, use_for_metrics: bool=True, commit: bool=True) -> Message:
  if message.guild is not None:
    users_repo.get_or_create_member_if_not_exist(message.author)
  else:
    users_repo.get_or_create_user_if_not_exist(message.author)

  item = Message.from_message(message)
  item.use_for_metrics = use_for_metrics
  session.add(item)

  if commit:
    session.commit()
  return item

def get_message(message_id: int) -> Optional[Message]:
  return session.query(Message).filter(Message.message_id == str(message_id)).one_or_none()

def get_message_metrics(guild_id: int, days_back: int) -> List[Tuple[int, datetime.datetime, int, int]]:
  threshold_date = datetime.datetime.utcnow() - datetime.timedelta(days=days_back)
  data = session.query(Message.message_id, Message.created_at, Message.author_id, Message.channel_id).filter(Message.created_at > threshold_date, Message.use_for_metrics == True, Message.guild_id == str(guild_id)).order_by(Message.created_at.desc()).all()
  return [(int(d[0]), d[1], int(d[2]), int(d[3])) for d in data]

def get_author_of_last_message_metric(channel_id: int, thread_id: Optional[int]) -> Optional[int]:
  user_id = session.query(Message.author_id).filter(Message.channel_id == str(channel_id), Message.thread_id == (str(thread_id) if thread_id is not None else None), Message.use_for_metrics == True).order_by(Message.created_at.desc()).first()
  return int(user_id[0]) if user_id is not None else None

def get_messages_of_member(member_id: int, guild_id: int, hours_back: float) -> List[Message]:
  threshold = datetime.datetime.utcnow() - datetime.timedelta(hours=hours_back)
  return session.query(Message).filter(Message.author_id == str(member_id), Message.guild_id == str(guild_id), Message.created_at > threshold).order_by(Message.created_at.desc()).all()

def delete_message(message_id: int, commit: bool=True):
  session.query(Message).filter(Message.message_id == str(message_id)).delete()
  if commit:
    session.commit()

def delete_old_messages(days: int):
  threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days)
  session.query(Message).filter(Message.created_at <= threshold).delete()
  session.commit()