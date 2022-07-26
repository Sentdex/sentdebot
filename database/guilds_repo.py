import disnake
from typing import Optional

from database import session
from database.tables.guilds import Guild

def get_guild(guild_id: int) -> Optional[Guild]:
  return session.query(Guild).filter(Guild.id == str(guild_id)).one_or_none()

def get_or_create_guild_if_not_exist(guild: disnake.Guild) -> Guild:
  guild_it = get_guild(guild.id)
  if guild_it is None:
    guild_it = Guild.from_guild(guild)
    session.add(guild_it)
    session.commit()
  return guild_it

def remove_guild(guild_id: int):
  session.query(Guild).filter(Guild.id == str(guild_id)).delete()
  session.commit()
