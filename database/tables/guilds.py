import disnake
from disnake.ext import commands
from typing import Optional
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from database import database

class Guild(database.base):
  __tablename__ = "guilds"

  id = Column(String, primary_key=True, unique=True, index=True)

  members = relationship("Member", back_populates="guild")
  audit_logs = relationship("AuditLog")

  @classmethod
  def from_guild(cls, guild: disnake.Guild):
    return cls(id=str(guild.id))

  async def to_object(self, bot: commands.Bot) -> Optional[disnake.Guild]:
    guild = bot.get_guild(int(self.id))
    if guild is None:
      try:
        guild = await bot.fetch_guild(int(self.id))
      except disnake.NotFound:
        return None
    return guild