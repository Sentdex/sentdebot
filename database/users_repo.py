import datetime

import disnake
from typing import Optional, List

from database import session
from database.tables.users import User

def get_user(user_id: int) -> Optional[User]:
  user = session.query(User).filter(User.id == str(user_id)).one_or_none()
  if user is not None and user.left_at is not None:
    user.left_at = None
    session.commit()
  return user

def create_user_if_not_exist(user: disnake.Member) -> User:
  user_it = get_user(user.id)
  if user_it is None:
    user_it = User(id=str(user.id), nick=user.display_name, created_at=user.created_at, joined_at=user.joined_at, icon_url=user.display_avatar.url)
    session.add(user_it)
    session.commit()
  return user_it

def delete_left_users(days_after_left: int):
  threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days_after_left)
  session.query(User).filter(User.left_at != None, User.left_at <= threshold).delete()
  session.commit()

def joined_in_timeframe(from_date: datetime.datetime, to_date: datetime.datetime) -> List[User]:
  return session.query(User).filter(User.joined_at >= from_date, User.joined_at <= to_date).order_by(User.joined_at.desc()).all()
