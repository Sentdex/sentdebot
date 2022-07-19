from typing import Optional, List
import datetime
import cachetools

from config import config
from database import session
from database.tables.help_threads import HelpThread

thread_cache = cachetools.LRUCache(config.db.max_number_of_cached_help_requests)

def get_thread(thread_id: int) -> Optional[HelpThread]:
  cached_item = thread_cache.get(thread_id)
  if cached_item is not None:
    return cached_item

  item = session.query(HelpThread).filter(HelpThread.thread_id == str(thread_id)).one_or_none()
  thread_cache[thread_id] = item
  return item

def thread_exists(thread_id: int):
  return get_thread(thread_id) is not None

def update_thread_activity(thread_id: int, new_activity: datetime.datetime, commit: bool=True):
  cached_item = thread_cache.get(thread_id)
  if cached_item is not None:
    cached_item.last_activity_time = new_activity
  else:
    session.query(HelpThread).filter(HelpThread.thread_id == str(thread_id)).update({HelpThread.last_activity_time : new_activity})

  if commit:
    session.commit()

def create_thread(thread_id: int, owner_id: int, tags: Optional[str]=None) -> HelpThread:
  item = HelpThread(thread_id=str(thread_id), owner_id=str(owner_id), tags=tags)
  session.add(item)
  session.commit()

  thread_cache[thread_id] = item
  return item

def get_all() -> List[HelpThread]:
  return session.query(HelpThread).order_by(HelpThread.last_activity_time.desc()).all()

def delete_thread(thread_id: int):
  session.query(HelpThread).filter(HelpThread.thread_id == str(thread_id)).delete()
  session.commit()

  if thread_id in thread_cache.keys():
    thread_cache.pop(thread_id)

def get_unactive(days_threshold: int) -> List[HelpThread]:
  date_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days_threshold)
  return session.query(HelpThread).filter(HelpThread.last_activity_time < date_threshold).all()

def delete_unactive(days_threshold: int):
  date_threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days_threshold)
  session.query(HelpThread).filter(HelpThread.last_activity_time < date_threshold).delete()
  session.commit()

  thread_cache.clear()

