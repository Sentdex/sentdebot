# Custom help cog

import math
import disnake as discord
from disnake.ext import commands

from config import config
from static_data.strings import Strings
from util import general_util
from features.paginator import EmbedView
from features.base_cog import Base_Cog
from util.logger import setup_custom_logger
from typing import Union, List

logger = setup_custom_logger(__name__)


def command_check(com, ctx):
  if not com.checks:
    return True

  for check in com.checks:
    try:
      if not check(ctx):
        return False
    except Exception:
      return False

  return True


def add_command_help(embed, com):
  help_string = f"**Help**: " + com.help if com.help is not None else ""
  brief = f"**Brief**: {com.brief}" if com.brief is not None else ""
  aliases = ("**Aliases**: " + ", ".join(com.aliases)) + "" if com.aliases else ""

  string_array = [it for it in [aliases, brief, help_string] if it != ""]
  output = "\n".join(string_array) if string_array else "*No description*"

  if len(output) > 4096:
    logger.warning(f"Description for command {com.name} is too long")
  else:
    embed.add_field(name=f"{config.command_prefixes[0]}{general_util.get_command_signature(com)}", value=output, inline=False)


def generate_help_for_cog(cog: Base_Cog, ctx: commands.Context) -> Union[None, List[discord.Embed]]:
  if cog.hidden and not general_util.is_administrator(ctx): return None

  coms = [com for com in cog.walk_commands() if isinstance(com, commands.Command) and not com.hidden and command_check(com, ctx)]
  number_of_coms = len(coms)
  if number_of_coms == 0: return None

  pages = []
  if number_of_coms > 10:
    number_of_batches = math.ceil(number_of_coms / 10)
    batches = [coms[i * 10: i * 10 + 10] for i in range(number_of_batches)]

    for idx, batch in enumerate(batches):
      emb = discord.Embed(title=f'{str(cog.qualified_name).replace("_", " ")} {idx + 1} Help', colour=discord.Color.green())
      general_util.add_author_footer(emb, ctx.author)

      for com in batch:
        add_command_help(emb, com)

      if len(emb) > 6000:
        logger.warning(f"Help for {cog.qualified_name} is too long")
      else:
        pages.append(emb)
  else:
    emb = discord.Embed(title=f'{str(cog.qualified_name)} Help', colour=discord.Color.green())
    general_util.add_author_footer(emb, ctx.author)

    for com in coms:
      add_command_help(emb, com)

    if len(emb) > 6000:
      logger.warning(f"Help for {cog.qualified_name} is too long")
    else:
      pages.append(emb)

  return pages


class Help(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Help, self).__init__(bot, __file__)

  @commands.command(brief=Strings.help_brief, help=Strings.help_help)
  @commands.cooldown(3, 20, commands.BucketType.user)
  async def help(self, ctx: commands.Context, *, module_name: str = None):
    await general_util.delete_message(self.bot, ctx)

    pages = []

    for cog in self.bot.cogs.values():
      if module_name is not None:
        if module_name.lower() != cog.qualified_name.lower() and \
            module_name.lower() != cog.file.lower() and \
            module_name.lower() != cog.file.lower().replace("_", " "):
          continue

      cog_pages = generate_help_for_cog(cog, ctx)
      if cog_pages is not None:
        pages.extend(cog_pages)

    if pages:
      await EmbedView(ctx.author, embeds=pages, perma_lock=True, remove_on_timeout=True).run(ctx)
    else:
      emb = discord.Embed(title="Help", description="*No help available*", colour=discord.Color.green())
      await ctx.send(embed=emb, delete_after=120)


def setup(bot):
  bot.add_cog(Help(bot))
