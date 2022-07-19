# Manager for help threads

import asyncio
import datetime
import disnake
from disnake.ext import commands, tasks
import math
from typing import Optional
import humanize

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
    if self.bot.is_ready():
      self.close_unactive_threads_task.start()

  def cog_unload(self) -> None:
    if self.close_unactive_threads_task.is_running():
      self.close_unactive_threads_task.cancel()

  def __del__(self):
    if self.close_unactive_threads_task.is_running():
      self.close_unactive_threads_task.cancel()

  @commands.Cog.listener()
  async def on_ready(self):
    if not self.close_unactive_threads_task.is_running():
      self.close_unactive_threads_task.start()

  @tasks.loop(hours=24)
  async def close_unactive_threads_task(self):
    logger.info("[Auto close task] Starting cleaning cycle")

    unactive_help_requests = help_threads_repo.get_unactive(config.help_threader.close_request_after_days_of_inactivity)
    help_channel: Optional[disnake.TextChannel] = self.bot.get_channel(config.ids.help_channel)

    if help_channel is None:
      logger.warning("[Auto close task] Help channel not found, skipping cycle")
      return

    for help_req_item in unactive_help_requests:
      message_id = int(help_req_item.thread_id)

      try:
        message = await help_channel.fetch_message(message_id)
      except:
        # Message that thread was connected to don't exist
        logger.info(f"[Auto close task] Message {message_id} don't exist")
        continue

      thread = message.thread
      if thread is None:
        # Thread don't exist
        logger.info(f"[Auto close task] Thread for message {message_id} don't exist")
        continue

      if thread.locked:
        # Thread is already closed
        logger.info(f"[Auto close task] Thread for message {message_id} is already closed")
        continue

      owner = message.guild.get_member(int(help_req_item.owner_id))
      if owner is None:
        # Owner of that thread is not on server anymore
        logger.info(f"[Auto close task] Owner of thread {thread.id} is not on server anymore, locking it up")
        try:
          await thread.edit(locked=True, archived=True, reason="Locking unactive thread")
        except:
          pass
        continue

      if thread.last_message_id is not None:
        try:
          last_message = await thread.fetch_message(thread.last_message_id)
        except:
          logger.info(f"[Auto close task] Last message of thread {thread.id} can't be retrieved so beliving data in database, locking it up")

          try:
            await thread.edit(locked=True, archived=True, reason="Locking unactive thread")
          except:
            pass
          continue

        last_activity_before = datetime.datetime.utcnow() - last_message.created_at

        if last_activity_before > datetime.timedelta(days=config.help_threader.close_request_after_days_of_inactivity):
          logger.info(f"[Auto close task] Last message of thread {thread.id} is older than {config.help_threader.close_request_after_days_of_inactivity} days, locking it up")
          try:
            await thread.edit(locked=True, archived=True, reason="Locking unactive thread")
          except:
            pass
        else:
          logger.info(f"[Auto close task] Last activity date for thread {thread.id} was outdated, updating it")

          if last_message.created_at > help_req_item.last_activity_time:
            help_req_item.last_activity_time = last_message.created_at

      # Some delay to easy the strain on discord api
      await asyncio.sleep(10)

      # Commit potential updates of last activity
    help_threads_repo.session.commit()

    help_threads_repo.delete_unactive(config.help_threader.close_request_after_days_of_inactivity)

    logger.info("[Auto close task] Cleaning cycle finished")


  async def create_new_help_thread(self, interaction: disnake.ModalInteraction, data:dict):
    title, tags, description = data["help_request:title"], data["help_request:tags"] if data["help_request:tags"] != "" else None, data["help_request:description"]
    help_channel: Optional[disnake.TextChannel] = self.bot.get_channel(config.ids.help_channel)

    if help_channel is None:
      return await general_util.generate_error_message(interaction, Strings.help_threader_help_channel_not_found)

    try:
      completed_message = f"{description}" if tags is None else f"{tags}\n{description}"
      message = await help_channel.send(completed_message)
      thread = await help_channel.create_thread(name=title, message=message, auto_archive_duration=1440, reason=f"Help request from {interaction.author}")
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

      if thread.locked:
        # Thread is closed
        logger.info(f"Thread for message {message_id} is closed")
        help_threads_repo.delete_thread(message_id)
        continue

      owner = message.guild.get_member(int(record.owner_id))
      if owner is None:
        # Owner of that thread is not on server anymore
        logger.info(f"Owner of thread {thread.id} is not on server anymore")
        help_threads_repo.delete_thread(message_id)
        continue

      if thread.archived:
        # Thread not active for extensive period of time but maybe still unsolved
        logger.info(f"Thread for message {message_id} is archived but not closed, skipping")
        continue

      unanswered_threads.append((thread, record.tags, message, owner, record.last_activity_time))

    if not unanswered_threads:
      embed = disnake.Embed(title="Help needed", description=Strings.help_threader_list_requests_no_help_required, color=disnake.Color.dark_green())
      general_util.add_author_footer(embed, inter.author)
      return await inter.send(embed=embed, ephemeral=True)

    num_of_unanswered_threads = len(unanswered_threads)
    number_of_batches = math.ceil(num_of_unanswered_threads / 5)
    batches = [unanswered_threads[i * 5 : i * 5 + 5] for i in range(number_of_batches)]

    pages = []
    for batch in batches:
      embed = disnake.Embed(title="Help needed", color=disnake.Color.dark_green())
      general_util.add_author_footer(embed, inter.author)
      for thread, tags, message, owner, last_activity in batch:
        tags = "".join([f"[{tag.strip()}]" for tag in tags.split(";") if tag != ""]) if tags is not None else None

        embed.add_field(name=f"{thread.name}", value=f"Owner: {owner.name}\nTags: {tags}\nLast activity: {humanize.naturaltime(last_activity)}\n[Link]({thread.jump_url})", inline=False)
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
      if not thread.archived and not thread.locked:
        await thread.edit(locked=True, archived=True, reason="Help request solved")
    except:
      pass

def setup(bot):
  bot.add_cog(HelpThreader(bot))
