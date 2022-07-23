import datetime

import disnake
from typing import Optional

from database import session
from database.tables.users import User

def get_user(user_id: int) -> Optional[User]:
  return session.query(User).filter(User.id == str(user_id)).one_or_none()

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
