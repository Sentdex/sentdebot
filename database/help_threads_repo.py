from typing import Optional, List

from database import session
from database.tables.help_threads import HelpThread

def get_thread(thread_id: int) -> Optional[HelpThread]:
  return session.query(HelpThread).filter(HelpThread.thread_id == str(thread_id)).one_or_none()

def create_thread(thread_id: int, owner_id: int, tags:Optional[str]=None) -> Optional[HelpThread]:
  if get_thread(thread_id) is not None: return None
  item = HelpThread(thread_id=str(thread_id), owner_id=str(owner_id), tags=tags)
  session.add(item)
  session.commit()
  return item

def get_all() -> List[HelpThread]:
  return session.query(HelpThread).all()

def delete_thread(message_id: int):
  session.query(HelpThread).filter(HelpThread.message_id == str(message_id)).delete()
  session.commit()
