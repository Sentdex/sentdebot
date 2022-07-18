# Custom help cog

import math
import disnake
from disnake.ext import commands

from config import config, cooldowns
from static_data.strings import Strings
from util import general_util
from features.paginator import EmbedView
from features.base_cog import Base_Cog
from util.logger import setup_custom_logger
from typing import Union, List, Optional

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

def get_all_commands(bot: commands.Bot, ctx):
  return [com for cog in bot.cogs.values() for com in cog.walk_commands() if isinstance(com, commands.Command) and not com.hidden and command_check(com, ctx)]

def add_command_help(embed, com):
  help_string = f"**Help**: " + com.help if com.help is not None else ""
  brief = f"**Brief**: {com.brief}" if com.brief is not None else ""
  aliases = ("**Aliases**: " + ", ".join(com.aliases)) + "" if com.aliases else ""

  string_array = [it for it in [aliases, brief, help_string] if it != ""]
  output = "\n".join(string_array) if string_array else "*No description*"

  if len(output) > 4096:
    logger.warning(f"Description for command {com.name} is too long")
  else:
    embed.add_field(name=f"{config.base.command_prefixes[0]}{general_util.get_command_signature(com)}", value=output, inline=False)


def generate_help_for_cog(cog: Base_Cog, ctx) -> Union[None, List[disnake.Embed]]:
  if cog.hidden and not general_util.is_administrator(ctx): return None

  coms = [com for com in cog.walk_commands() if isinstance(com, commands.Command) and not com.hidden and command_check(com, ctx)]
  number_of_coms = len(coms)
  if number_of_coms == 0: return None

  pages = []
  if number_of_coms > 10:
    number_of_batches = math.ceil(number_of_coms / 10)
    batches = [coms[i * 10: i * 10 + 10] for i in range(number_of_batches)]

    for idx, batch in enumerate(batches):
      emb = disnake.Embed(title=f'{str(cog.qualified_name).replace("_", " ")} {idx + 1} Help', colour=disnake.Color.green())
      general_util.add_author_footer(emb, ctx.author)

      for com in batch:
        add_command_help(emb, com)

      if len(emb) > 6000:
        logger.warning(f"Help for {cog.qualified_name} is too long")
      else:
        pages.append(emb)
  else:
    emb = disnake.Embed(title=f'{str(cog.qualified_name)} Help', colour=disnake.Color.green())
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

  @commands.command(name="help", brief=Strings.help_dummy_help_brief)
  async def dummy_help(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)
    embed = disnake.Embed(title="Help", description=Strings.help_dummy_help_text, colour=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)
    await ctx.send(embed=embed)

  @commands.slash_command(name="help", description=Strings.help_description)
  @cooldowns.short_cooldown
  async def help(self, inter: disnake.CommandInteraction, name: Optional[str]=commands.Param(default=None, description="Name of command or extension you want to search help for")):
    pages = []
    if name is not None:
      all_commands = get_all_commands(self.bot, inter)
      command = disnake.utils.get(all_commands, name=name)
      if command is not None:
        emb = disnake.Embed(title="Help", colour=disnake.Color.green())
        general_util.add_author_footer(emb, inter.author)
        add_command_help(emb, command)
        return await inter.send(embed=emb, ephemeral=True)

    for cog in self.bot.cogs.values():
      if name is not None:
        if name.lower() != cog.qualified_name.lower() and \
            name.lower() != cog.file.lower() and \
            name.lower() != cog.file.lower().replace("_", " "):
          continue

      cog_pages = generate_help_for_cog(cog, inter)
      if cog_pages is not None:
        pages.extend(cog_pages)

    if pages:
      await EmbedView(inter.author, embeds=pages, perma_lock=True).run(inter)
    else:
      emb = disnake.Embed(title="Help", description="*No help available*", colour=disnake.Color.orange())
      await inter.send(embed=emb, ephemeral=True)

  @commands.slash_command(name="command_list", description=Strings.help_commands_list_description)
  @cooldowns.short_cooldown
  async def command_list(self, inter: disnake.CommandInteraction):
    all_commands = get_all_commands(self.bot, inter)
    command_strings = [f"{config.base.command_prefixes[0]}{general_util.get_command_signature(com)}" for com in all_commands]

    pages = []
    while command_strings:
      output, command_strings = general_util.add_string_until_length(command_strings, 4000, "\n")
      embed = disnake.Embed(title="Commands list", description=output, colour=disnake.Color.dark_blue())
      general_util.add_author_footer(embed, inter.author)
      pages.append(embed)

    if pages:
      await EmbedView(inter.author, embeds=pages, perma_lock=True).run(inter)
    else:
      emb = disnake.Embed(title="Commands list", description="*No commands available*", colour=disnake.Color.orange())
      await inter.send(embed=emb, ephemeral=True)

def setup(bot):
  bot.add_cog(Help(bot))
