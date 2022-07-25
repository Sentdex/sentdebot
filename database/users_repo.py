import datetime

import disnake
from typing import Optional, List, Union

from database import session
from database.tables.users import User, Member
from database import guilds_repo

def get_user(user_id: int) -> Optional[User]:
  return session.query(User).filter(User.id == str(user_id)).one_or_none()

def get_member(member_id: int, guild_id: int) -> Optional[Member]:
  member = session.query(Member).filter(Member.id == str(member_id), Member.guild_id == str(guild_id)).one_or_none()
  if member is not None and member.left_at is not None:
    member.left_at = None
    session.commit()
  return member

def get_or_create_user_if_not_exist(user: Union[disnake.Member, disnake.User]) -> User:
  user_it = get_user(user.id)
  if user_it is None:
    user_it = User.from_user(user)
    session.add(user_it)
    session.commit()
  return user_it

def get_or_create_member_if_not_exist(member: disnake.Member) -> Member:
  member_it = get_member(member.id, member.guild.id)

  if member_it is None:
    get_or_create_user_if_not_exist(member)
    guilds_repo.get_or_create_guild_if_not_exist(member.guild)

    member_it = Member.from_member(member)
    session.add(member_it)
    session.commit()
  return member_it

def delete_left_members(days_after_left: int):
  threshold = datetime.datetime.utcnow() - datetime.timedelta(days=days_after_left)
  session.query(Member).filter(Member.left_at != None, Member.left_at <= threshold).delete()
  session.commit()

def members_joined_in_timeframe(from_date: datetime.datetime, to_date: datetime.datetime, guild_id: int) -> List[Member]:
  return session.query(Member).filter(Member.joined_at >= from_date, Member.joined_at <= to_date, Member.guild_id == str(guild_id)).order_by(Member.joined_at.desc()).all()
