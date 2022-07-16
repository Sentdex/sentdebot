import disnake
from disnake.ext import commands

from features.base_cog import Base_Cog
from config import config

class AutoThreader(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(AutoThreader, self).__init__(bot, __file__)

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.author.bot: return
    if message.guild is None: return

    if message.channel.id in config.auto_threader_channel_ids:
      # Auto archive set to 3 days
      await message.create_thread(name="Automatic thread", auto_archive_duration=4320, reason="Automatic thread")

def setup(bot):
  bot.add_cog(AutoThreader(bot))
