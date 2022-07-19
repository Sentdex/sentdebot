# Precursor for extension
import disnake
from disnake.ext import commands
from pathlib import Path
from typing import Optional

from features.reaction_context import ReactionContext

class Base_Cog(commands.Cog):
  def __init__(self, bot:commands.Bot, file:str, hidden:bool=False):
    self.bot = bot
    self.file = str(Path(file).stem) # Stores filename of that extension for later use in extension manipulating extensions and help
    self.hidden = hidden

  async def handle_reaction_add(self, ctx: ReactionContext):
    pass

  async def handle_message_edited(self, before: Optional[disnake.Message], after: disnake.Message):
    pass
