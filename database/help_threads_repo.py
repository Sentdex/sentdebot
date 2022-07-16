from typing import Optional, List

from database import session
from database.tables.help_threads import HelpThread

def get_thread(message_id: int) -> Optional[HelpThread]:
  return session.query(HelpThread).filter(HelpThread.message_id == str(message_id)).one_or_none()

def create_thread(channel_id: int, message_id: int, owner_id: int) -> Optional[HelpThread]:
  if get_thread(message_id) is not None: return None
  item = HelpThread(message_id=str(message_id), channel_id=str(channel_id), owner_id=str(owner_id))
  session.add(item)
  session.commit()
  return item

def get_all() -> List[HelpThread]:
  return session.query(HelpThread).all()

def delete_all_from_channel(channel_id: int):
  session.query(HelpThread).filter(HelpThread.channel_id == str(channel_id)).delete()
  session.commit()

def delete_thread(message_id: int):
  session.query(HelpThread).filter(HelpThread.message_id == str(message_id)).delete()
  session.commit()
