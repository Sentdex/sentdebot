import disnake
from disnake.ext import commands
import random
import traceback

from features.base_cog import Base_Cog
from config import config
from util.logger import setup_custom_logger

logger = setup_custom_logger(__name__)


def have_random_role(member: disnake.Member):
  for role in member.roles:
    if role.id in config.random_role_giver.role_ids:
      return True
  return False


class RandomRoleGiver(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(RandomRoleGiver, self).__init__(bot, __file__)

    self.chance = max(min(config.random_role_giver.chance, 100), 0)
    self.range = int((1 / self.chance if self.chance > 0 else 0) * 100) - 1

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if not config.random_role_giver.role_ids: return
    if message.author.bot: return
    if have_random_role(message.author): return
    if self.chance == 0: return

    guild = self.bot.get_guild(config.ids.main_guild)
    if guild is None:
      return

    roll = random.randint(0, self.range)
    # logger.info(f"Roll value: {roll}")
    if roll == 0:
      selected_role_id = random.choice(config.random_role_giver.role_ids)
      selected_role = guild.get_role(selected_role_id)
      if selected_role is None:
        logger.warning(f"Role with id '{selected_role_id}' doesn't exist in main guild")
        return

      try:
        await message.author.add_roles(selected_role, reason="Random role assigned by bot")
        logger.info(f"User {message.author.name} was awarded with {selected_role.name} role")
      except Exception as e:
        logger.error(f"Failed to give user {message.author.display_name} {selected_role.name} ({selected_role_id}) role\n{traceback.format_exc()}")

def setup(bot):
  bot.add_cog(RandomRoleGiver(bot))
