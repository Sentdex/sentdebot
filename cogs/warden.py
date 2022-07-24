import datetime
import disnake
from disnake.ext import commands
from typing import Optional, List
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

CONTENT_MEDIUM_SIMILARITY = 85
CONTENT_HIGH_SIMILARITY = 95

ATT_MEDIUM_SIMILARITY_PROBABILITY = 85
ATT_HIGH_SIMILARITY_PROBABILITY = 95

message_cache = cachetools.FIFOCache(config.warden.message_cache_size)

@dataclasses.dataclass
class WardenMessageData:
  message_id: int
  channel_id: int
  thread_id: Optional[int]
  created_at: datetime.datetime

  content: Optional[str]

  attachment_hashes: List[str]

  def __eq__(self, other):
    if other is None: return False
    if other.message_id == self.message_id:
      return True
    return False

class Warden(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Warden, self).__init__(bot, __file__)

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

  async def calculate_hashes_of_attachments(self, message: disnake.Message) -> List[str]:
    att_hashes = []
    for f in message.attachments:
      fp = io.BytesIO()
      await f.save(fp)

      att_hash = hashlib.md5(fp.read()).hexdigest()
      att_hashes.append(str(att_hash))
    return att_hashes

  async def generate_message_hash(self, message: disnake.Message) -> WardenMessageData:
    att_hashes = await self.calculate_hashes_of_attachments(message)

    channel_id = message.channel.id
    thread_id = None
    if isinstance(message.channel, disnake.Thread):
      channel_id = message.channel.parent.id
      thread_id = message.channel.id

    item = WardenMessageData(message.id, channel_id, thread_id, message.created_at, message.content, att_hashes)
    message_cache[message.id] = item
    return item

  async def check_for_duplicates(self, message: disnake.Message):
    def hamming_distance(chaine1, chaine2):
      return sum(c1 != c2 for c1, c2 in zip(chaine1, chaine2))

    current_message = await self.generate_message_hash(message)
    current_have_attachments = len(current_message.attachment_hashes) != 0
    all_messages: List[WardenMessageData] = list(message_cache.values())

    content_max_similarity = 0
    similar_object = None

    attachments_present = False
    attachment_max_probability = 0

    for message_item in all_messages:
      if message_item == current_message:
        continue

      if current_message.content is not None and message_item.content is not None:
        content_similarity = ratio(current_message.content, message_item.content) * 100
        logger.info(f"Content similarity: {content_similarity}")

        if content_similarity > content_max_similarity:
          content_max_similarity = content_similarity
          similar_object = message_item

          attachment_max_probability = 0
          attachments_present = len(message_item.attachment_hashes) != 0

          if attachments_present:
            for message_attachment_hash in message_item.attachment_hashes:
              for cur_message_attachment_hash in current_message.attachment_hashes:
                att_hammin = hamming_distance(int(message_attachment_hash), int(cur_message_attachment_hash))

                probability = (1 - att_hammin / 128) * 100
                logger.info(f"Attachment duplicate probability: {probability}")

                if probability > attachment_max_probability:
                  attachment_max_probability = probability

    if content_max_similarity >= CONTENT_MEDIUM_SIMILARITY and ((not attachments_present and not current_have_attachments) or attachment_max_probability >= ATT_MEDIUM_SIMILARITY_PROBABILITY):
      await self.announce_duplicate(message, similar_object, content_max_similarity, attachment_max_probability)

  async def announce_duplicate(self, message: disnake.Message, similar_object: WardenMessageData, content_similarity: float, attachment_probability: float):
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

    description = f"Content similarity: {content_similarity}%"
    if attachment_probability > 0:
      description += f"\nAttachment duplicate probability: {attachment_probability}%"
    description = description.strip()

    color = disnake.Color.orange() if content_similarity < CONTENT_HIGH_SIMILARITY and attachment_probability < ATT_HIGH_SIMILARITY_PROBABILITY else disnake.Color.red()
    embed = disnake.Embed(title="Message duplicate found", color=color, description=description)
    embed.add_field(name="Original message", value=f"[Link]({original_message.jump_url})" if original_message is not None else "_??? (404)_")
    embed.add_field(name="Duplicate message", value=f"[Link]({message.jump_url})")

    await report_channel.send(embed=embed)


def setup(bot):
  bot.add_cog(Warden(bot))
