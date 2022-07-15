from disnake.ext import commands
from pathlib import Path

class Base_Cog(commands.Cog):
  def __init__(self, bot:commands.Bot, file:str, hidden:bool=False):
    self.bot = bot
    self.file = str(Path(file).stem)
    self.hidden = hidden