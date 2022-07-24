import datetime
import disnake
from disnake.ext import commands, tasks
from typing import Optional, List, Dict
import io
from Levenshtein import ratio
import hashlib
import cachetools
import dataclasses

from config import config
from features.base_cog import Base_Cog
from util.logger import setup_custom_logger
from util import general_util

logger = setup_custom_logger(__name__)

CONTENT_MEDIUM_SIMILARITY = 90
CONTENT_HIGH_SIMILARITY = 95

message_cache = cachetools.FIFOCache(config.warden.message_cache_size)

@dataclasses.dataclass
class WardenMessageData:
  author_id: int
  message_id: int
  channel_id: int
  thread_id: Optional[int]
  created_at: datetime.datetime

  content: str

  attachment_hashes: List[str]

  def __eq__(self, other):
    if other is None: return False
    if other.message_id == self.message_id:
      return True
    return False


async def calculate_hashes_of_attachments(message: disnake.Message) -> List[str]:
  att_hashes = []
  for f in message.attachments:
    fp = io.BytesIO()
    await f.save(fp)

    att_hash = hashlib.md5(fp.read()).hexdigest()
    att_hashes.append(str(att_hash))
  return att_hashes


async def generate_message_hash(message: disnake.Message) -> WardenMessageData:
  channel_id = message.channel.id
  thread_id = None
  if isinstance(message.channel, disnake.Thread):
    channel_id = message.channel.parent.id
    thread_id = message.channel.id

  att_hashes = await calculate_hashes_of_attachments(message)

  item = WardenMessageData(message.author.id, message.id, channel_id, thread_id, datetime.datetime.utcnow(), message.content, att_hashes)
  message_cache[message.id] = item
  return item


class Warden(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Warden, self).__init__(bot, __file__)

    self.strikes: Dict[int, int] = {}
    self.decrement_strikes_task.start()

  def cog_unload(self) -> None:
    if self.decrement_strikes_task.is_running():
      self.decrement_strikes_task.cancel()

  def __del__(self):
    if self.decrement_strikes_task.is_running():
      self.decrement_strikes_task.cancel()

  @tasks.loop(minutes=config.warden.decrement_strikes_every_minutes)
  async def decrement_strikes_task(self):
    keys = self.strikes.keys()
    for key in keys:
      self.strikes[key] -= 1
      if self.strikes[key] <= 0:
        del self.strikes[key]

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.author.bot: return
    if isinstance(message.channel, disnake.DMChannel): return
    if message.guild.id != config.ids.main_guild: return
    if message.channel.id not in config.ids.warden_channels_to_look_for: return

    await self.check_for_duplicates(message)

  @commands.Cog.listener()
  async def on_raw_bulk_message_delete(self, payload: disnake.RawBulkMessageDeleteEvent):
    if payload.guild_id is None: return
    if payload.guild_id != config.ids.main_guild: return
    if payload.guild_id not in config.ids.warden_channels_to_look_for: return

    for message_id in payload.message_ids:
      if message_id in message_cache.keys():
        message_cache.pop(message_id)

  @commands.Cog.listener()
  async def on_raw_message_delete(self, payload: disnake.RawMessageDeleteEvent):
    if payload.guild_id is None: return
    if payload.guild_id != config.ids.main_guild: return
    if payload.guild_id not in config.ids.warden_channels_to_look_for: return

    if payload.message_id in message_cache.keys():
      message_cache.pop(payload.message_id)

  async def check_for_duplicates(self, message: disnake.Message):
    logger.info("Starting message duplicate check")
    current_message = await generate_message_hash(message)
    all_messages: List[WardenMessageData] = list(message_cache.values())

    content_max_similarity = 0
    similar_object = None
    att_similar_object = None

    for message_item in all_messages:
      if message_item == current_message:
        continue

      if datetime.datetime.utcnow() - message_item.created_at > datetime.timedelta(minutes=config.warden.expire_time_minutes):
        message_cache.pop(message_item.message_id)
        continue

      if message_item.author_id != current_message.author_id:
        continue

      content_similarity = ratio(current_message.content, message_item.content) * 100
      logger.info(f"Content similarity: {content_similarity}")

      if content_similarity > content_max_similarity:
        content_max_similarity = content_similarity
        similar_object = message_item

      for message_attachment_hash in message_item.attachment_hashes:
        for cur_message_attachment_hash in current_message.attachment_hashes:
          if cur_message_attachment_hash == message_attachment_hash:
            att_similar_object = message_item

    logger.info("Duplicate check finished")

    if content_max_similarity >= CONTENT_MEDIUM_SIMILARITY or att_similar_object is not None:
      if message.author.id in self.strikes.keys():
        self.strikes[message.author.id] += 1
      else:
        self.strikes[message.author.id] = 1

      if self.strikes[message.author.id] >= config.warden.strikes_to_notify:
        if content_max_similarity >= CONTENT_MEDIUM_SIMILARITY:
          await self.announce_content_duplicate(message, similar_object, content_max_similarity)
        if att_similar_object is not None and att_similar_object != similar_object:
          await self.announce_attachment_duplicate(message, att_similar_object)

  async def announce_content_duplicate(self, message: disnake.Message, similar_object: WardenMessageData, content_similarity: float):
    report_channel = await general_util.get_or_fetch_channel(self.bot, config.ids.warden_report_channel)
    if report_channel is None:
      logger.warning("Failed to get announce channel")
      return

    original_message_channel = await general_util.get_or_fetch_channel(message.guild, similar_object.channel_id if similar_object.thread_id is None else similar_object.thread_id)
    if original_message_channel is None:
      logger.warning("Failed to find original message channel")
      message_cache.pop(similar_object.message_id)
      return

    original_message = await general_util.get_or_fetch_message(self.bot, original_message_channel, similar_object.message_id)

    color = disnake.Color.orange() if content_similarity < CONTENT_HIGH_SIMILARITY else disnake.Color.red()
    embed = disnake.Embed(title="Message duplicate found", color=color, description=f"Content similarity: {content_similarity}%")
    embed.add_field(name="Author", value=f"Author: {original_message.author}", inline=False)
    embed.add_field(name="Original message", value=f"Channel: {original_message.channel.name}\n[Link]({original_message.jump_url})" if original_message is not None else "_??? (404)_")
    embed.add_field(name="Duplicate message", value=f"Channel: {message.channel.name}\n[Link]({message.jump_url})")

    await report_channel.send(embed=embed)

  async def announce_attachment_duplicate(self, message: disnake.Message, similar_object: WardenMessageData):
    report_channel = await general_util.get_or_fetch_channel(self.bot, config.ids.warden_report_channel)
    if report_channel is None:
      logger.warning("Failed to get announce channel")
      return

    original_message_channel = await general_util.get_or_fetch_channel(message.guild, similar_object.channel_id if similar_object.thread_id is None else similar_object.thread_id)
    if original_message_channel is None:
      logger.warning("Failed to find original message channel")
      message_cache.pop(similar_object.message_id)
      return

    original_message = await general_util.get_or_fetch_message(self.bot, original_message_channel, similar_object.message_id)

    embed = disnake.Embed(title="Message duplicate found", color=disnake.Color.red(), description="Attachment is the same")
    embed.add_field(name="Author", value=f"Author: {original_message.author}", inline=False)
    embed.add_field(name="Original message", value=f"Channel: {original_message.channel.name}\n[Link]({original_message.jump_url})" if original_message is not None else "_??? (404)_")
    embed.add_field(name="Duplicate message", value=f"Channel: {message.channel.name}\n[Link]({message.jump_url})")

    await report_channel.send(embed=embed)


def setup(bot):
  bot.add_cog(Warden(bot))
