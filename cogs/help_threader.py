# Manager for help threads

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
from modals.create_help_request import HelpRequestModal

logger = setup_custom_logger(__name__)

class HelpThreader(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(HelpThreader, self).__init__(bot, __file__)

  async def create_new_help_thread(self, interaction: disnake.ModalInteraction, data:dict):
    title, tags, description = data["title"], data["tags"] if data["tags"] != "" else None, data["description"]
    help_channel: Optional[disnake.TextChannel] = self.bot.get_channel(config.ids.help_channel)

    if help_channel is None:
      return await general_util.generate_error_message(interaction, Strings.help_threader_help_channel_not_found)

    try:
      completed_message = f"{description}" if tags is None else f"{tags}\n{description}"
      message = await help_channel.send(completed_message)
      # Archive after 3 day
      thread = await help_channel.create_thread(name=title, message=message, auto_archive_duration=4320, reason=f"Help request from {interaction.author}")
      await thread.add_user(interaction.author)

      help_threads_repo.create_thread(thread.id, interaction.author.id, tags)

      await thread.send(Strings.help_threader_announcement)
    except disnake.HTTPException:
      return await general_util.generate_error_message(interaction, Strings.help_threader_request_create_failed)

    await general_util.generate_success_message(interaction, Strings.help_threader_request_create_passed(link=thread.jump_url))

  @commands.slash_command(name="help_requests")
  async def help_requests(self, inter: disnake.CommandInteraction):
    pass

  @help_requests.sub_command(name="create", description=Strings.help_threader_request_create_brief)
  @cooldowns.huge_cooldown
  async def help_requests_create(self, inter: disnake.CommandInteraction):
    await inter.response.send_modal(HelpRequestModal(self.create_new_help_thread))

  @help_requests.sub_command(name="list", description=Strings.help_threader_list_requests_brief)
  @cooldowns.long_cooldown
  async def help_requests_list(self, inter: disnake.CommandInteraction):
    unanswered_threads = []
    all_records = help_threads_repo.get_all()
    help_channel: Optional[disnake.TextChannel] = self.bot.get_channel(config.ids.help_channel)

    if help_channel is None:
      return await general_util.generate_error_message(inter, Strings.help_threader_help_channel_not_found)

    for record in all_records:
      message_id = int(record.thread_id)

      try:
        message = await help_channel.fetch_message(message_id)
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

      unanswered_threads.append((thread, record.tags, message, owner))

    if not unanswered_threads:
      embed = disnake.Embed(title="Help needed", description=Strings.help_threader_list_requests_no_help_required, color=disnake.Color.dark_green())
      return await inter.send(embed=embed, ephemeral=True)

    num_of_unanswered_threads = len(unanswered_threads)
    number_of_batches = math.ceil(num_of_unanswered_threads / 5)
    batches = [unanswered_threads[i * 5 : i * 5 + 5] for i in range(number_of_batches)]

    pages = []
    for batch in batches:
      embed = disnake.Embed(title="Help needed", color=disnake.Color.dark_green())
      for thread, tags, message, owner in batch:
        embed.add_field(name=f"{thread.name}", value=f"Owner: {owner.name}\nTags: {tags}\n[Link]({thread.jump_url})", inline=False)
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

    try:
      # Archive thread
      help_channel: Optional[disnake.TextChannel] = self.bot.get_channel(config.ids.help_channel)
      message = await help_channel.fetch_message(thread_message_id)
      thread = message.thread
      await thread.edit(archived=True)
    except:
      pass

def setup(bot):
  bot.add_cog(HelpThreader(bot))
