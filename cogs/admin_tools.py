import asyncio
import disnake
from disnake.ext import commands
from typing import Union

from features.base_cog import Base_Cog
from util import general_util
from database import messages_repo, users_repo
from static_data.strings import Strings

class AdminTools(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(AdminTools, self).__init__(bot, __file__)

  async def delete_users_messages(self, user_id: int, hours_back: float):
    delete_message_count = 0

    messages = messages_repo.get_messages_of_user(user_id, hours_back)
    for message_it in messages:
      channel = await general_util.get_or_fetch_channel(self.bot, int(message_it.channel_id) if message_it.thread_id is None else int(message_it.thread_id))
      if channel is None: continue
      message = await general_util.get_or_fetch_message(self.bot, channel, int(message_it.message_id))
      if message is None: continue

      try:
        await message.delete()
        await asyncio.sleep(0.1)
        delete_message_count += 1
      except disnake.NotFound:
        pass

    return delete_message_count

  @commands.command(brief=Strings.admin_tools_clean_raid_brief, help=Strings.admin_tools_clean_raid_help)
  @commands.check(general_util.is_mod)
  async def clean_raid(self, ctx: commands.Context, first_message: Union[disnake.Message, int], last_message: Union[disnake.Message, int], hours_back: float = 1.0):
    if hours_back <= 0:
      return await general_util.generate_error_message(ctx, Strings.admin_tools_invalid_hours_back)

    if isinstance(first_message, int):
      first_message = await general_util.get_or_fetch_message(self.bot, ctx.channel, first_message)
    if isinstance(last_message, int):
      last_message = await general_util.get_or_fetch_message(self.bot, ctx.channel, last_message)

    if first_message is None or last_message is None:
      return await general_util.generate_error_message(ctx, Strings.admin_tools_clean_raid_messages_not_found)

    joined_users_items = users_repo.joined_in_timeframe(first_message.author.joined_at, last_message.author.joined_at)

    statuses = []
    some_failed = False
    for user_it in joined_users_items:
      delete_message_count = await self.delete_users_messages(int(user_it.id), hours_back)
      statuses.append(f"{user_it.nick} - Deleted {delete_message_count} messages")

    embed = disnake.Embed(title="Clean raid report", description=general_util.truncate_string("\n".join(statuses), 4000), color=disnake.Color.orange() if some_failed else disnake.Color.green())
    general_util.add_author_footer(embed, ctx.author)

    await ctx.send(embed=embed)

  @commands.command(brief=Strings.admin_tools_destroy_raid_brief, help=Strings.admin_tools_destroy_raid_help)
  @commands.check(general_util.is_mod)
  async def destroy_raid(self, ctx: commands.Context, first_message: Union[disnake.Message, int], last_message: Union[disnake.Message, int], hours_back: float=1.0):
    if isinstance(first_message, int):
      first_message = await general_util.get_or_fetch_message(self.bot, ctx.channel, first_message)
    if isinstance(last_message, int):
      last_message = await general_util.get_or_fetch_message(self.bot, ctx.channel, last_message)

    if first_message is None or last_message is None:
      return await general_util.generate_error_message(ctx, Strings.admin_tools_destroy_raid_messages_not_found)

    joined_users_items = users_repo.joined_in_timeframe(first_message.author.joined_at, last_message.author.joined_at)

    statuses = []
    some_failed = False
    for user_it in joined_users_items:
      delete_message_count = None
      if hours_back > 0:
        delete_message_count = await self.delete_users_messages(int(user_it.id), hours_back)

      member = await general_util.get_or_fetch_member(ctx.guild, int(user_it.id))
      if member is None:
        statuses.append(f"{user_it.nick} not banned (not found)" + f" - Deleted {delete_message_count} messages" if delete_message_count is not None else "")
        some_failed = True
      else:
        try:
          await member.ban()
        except:
          statuses.append(f"{user_it.nick} not banned (unable)" + f" - Deleted {delete_message_count} messages" if delete_message_count is not None else "")
          some_failed = True
          continue

        statuses.append(f"{user_it.nick} banned" + f" - Deleted {delete_message_count} messages" if delete_message_count is not None else "")

    embed = disnake.Embed(title="Destroy raid report", description=general_util.truncate_string("\n".join(statuses), 4000), color=disnake.Color.orange() if some_failed else disnake.Color.green())
    general_util.add_author_footer(embed, ctx.author)

    await ctx.send(embed=embed)

  @commands.command(brief=Strings.admin_tools_clean_user_brief, help=Strings.admin_tools_clean_user_help)
  @commands.check(general_util.is_mod)
  async def clean_user(self, ctx: commands.Context, user: Union[disnake.Member, disnake.User, int], hours_back: float = 1.0):
    if hours_back <= 0:
      return await general_util.generate_error_message(ctx, Strings.admin_tools_invalid_hours_back)
    delete_message_count = await self.delete_users_messages(user if isinstance(user, int) else user.id, hours_back)
    await general_util.generate_success_message(ctx, f"User's messages cleaned\nDeleted `{delete_message_count}` messages")

  @commands.command(brief=Strings.admin_tools_destroy_user_brief, help=Strings.admin_tools_destroy_user_help)
  @commands.check(general_util.is_mod)
  async def destroy_user(self, ctx: commands.Context, user: Union[disnake.Member, disnake.User, int], hours_back: float = 1.0):
    delete_message_count = None
    if hours_back > 0:
      delete_message_count = await self.delete_users_messages(user if isinstance(user, int) else user.id, hours_back)

    await user.ban()
    await general_util.generate_success_message(ctx, "User destroyed" + (f"\nDeleted `{delete_message_count}` messages" if delete_message_count is not None else ""))

def setup(bot):
  bot.add_cog(AdminTools(bot))