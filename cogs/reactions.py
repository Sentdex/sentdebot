from disnake.ext import commands
from typing import List
import asyncio
import traceback

from features.base_cog import Base_Cog
from features.reaction_context import ReactionContext
from util.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class Reactions(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Reactions, self).__init__(bot, __name__)

  @commands.Cog.listener()
  async def on_raw_reaction_add(self, payload):
    ctx: ReactionContext = await ReactionContext.from_payload(self.bot, payload)
    if ctx is None:
      return

    cogs:List[Base_Cog] = self.bot.cogs.values()
    try:
      cogs_listening_futures = [cog.handle_reaction_add(ctx) for cog in cogs]
      await asyncio.gather(*cogs_listening_futures)
    except:
      logger.warning(f"Failed to execute add reaction handler\n{traceback.format_exc()}")

def setup(bot):
  bot.add_cog(Reactions(bot))
