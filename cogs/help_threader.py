import disnake
from disnake.ext import commands
import math
from typing import Optional

from features.base_cog import Base_Cog
from config import config, cooldowns
from static_data.strings import Strings
from features.paginator import EmbedView
from database import help_threads_repo
from util.logger import setup_custom_logger
from util import general_util

logger = setup_custom_logger(__name__)

class HelpThreader(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(HelpThreader, self).__init__(bot, __file__)

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.author.bot: return
    if message.guild is None: return
    if not isinstance(message.channel, disnake.TextChannel): return

    if message.channel.id in config.base_help_channel_ids:

      # Auto archive set to 3 days
      try:
        thread = await message.create_thread(name="Automatic thread", auto_archive_duration=4320, reason="Automatic thread")
        help_threads_repo.create_thread(message.channel.id, message.id, message.author.id)
        await thread.send(Strings.help_threader_announcement)
        await thread.leave()
      except disnake.HTTPException:
        pass

  @commands.slash_command(name="help_requests")
  async def help_requests(self, inter: disnake.CommandInteraction):
    pass

  @help_requests.sub_command(name="list", description=Strings.help_threader_list_requests_brief)
  @cooldowns.long_cooldown
  async def help_requests_list(self, inter: disnake.CommandInteraction):
    unanswered_threads = []
    all_records = help_threads_repo.get_all()

    for record in all_records:
      message_id = int(record.message_id)

      channel: Optional[disnake.TextChannel] = self.bot.get_channel(int(record.channel_id))
      if channel is None:
        # Channel don't exist
        logger.info(f"Channel {record.channel_id} don't exist")
        help_threads_repo.delete_all_from_channel(int(record.channel_id))
        continue

      try:
        message = await channel.fetch_message(message_id)
      except:
        # Message that thread was connected to don't exist
        logger.info(f"Message {message_id} don't exist")
        help_threads_repo.delete_thread(message_id)
        continue

      thread = message.thread
      if thread is None:
        # Thread don't exist
        logger.info(f"Thread for message {message_id} don't exist")
        help_threads_repo.delete_thread(message_id)
        continue

      if thread.locked or thread.archived:
        # Thread is unactive or closed
        logger.info(f"Thread for message {message_id} is closed")
        help_threads_repo.delete_thread(message_id)
        continue

      owner = message.guild.get_member(int(record.owner_id))
      if owner is None:
        # Owner of that thread is not on server anymore
        logger.info(f"Owner of thread {thread.id} is not on server anymore")
        help_threads_repo.delete_thread(message_id)
        continue

      unanswered_threads.append((thread, message, owner))

    if not unanswered_threads:
      embed = disnake.Embed(title="Help needed", description=Strings.help_threader_list_requests_no_help_required, color=disnake.Color.dark_green())
      return await inter.send(embed=embed, ephemeral=True)

    num_of_unanswered_threads = len(unanswered_threads)
    number_of_batches = math.ceil(num_of_unanswered_threads / 10)
    batches = [unanswered_threads[i * 10 : i * 10 + 10] for i in range(number_of_batches)]

    pages = []
    for batch in batches:
      embed = disnake.Embed(title="Help needed", color=disnake.Color.dark_green())
      for thread, message, owner in batch:
        embed.add_field(name=f"{thread.name}", value=f"Owner: {owner.name}\n[Link]({thread.jump_url})", inline=False)
      pages.append(embed)

    await EmbedView(inter.author, pages).run(inter)

  @help_requests.sub_command(name="solved", description=Strings.help_threader_request_solved_brief)
  async def help_requests_solved(self, inter: disnake.CommandInteraction):
    thread_message_id = inter.channel_id
    record = help_threads_repo.get_thread(thread_message_id)

    if record is None:
      return await general_util.generate_error_message(inter, Strings.help_threader_request_solved_not_found)

    if int(record.owner_id) != inter.author.id and not general_util.is_mod(inter):
      return await general_util.generate_error_message(inter, Strings.help_threader_request_solved_not_owner)

    help_threads_repo.delete_thread(thread_message_id)
    await general_util.generate_success_message(inter, Strings.help_threader_request_solved_closed)

def setup(bot):
  bot.add_cog(HelpThreader(bot))
