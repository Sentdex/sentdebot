import math
import disnake
from disnake.ext import commands
from typing import Union, Iterable
import os
from datetime import datetime, timezone

from config import config

def is_administrator(ctx: commands.Context):
  if not isinstance(ctx.author, disnake.Member):
    return False

  if disnake.utils.get(ctx.author.roles, id=config.admin_role_id) is not None or ctx.author.id == ctx.guild.owner_id:
    return True
  return False

def is_mod(ctx: commands.Context):
  if not isinstance(ctx.author, disnake.Member):
    return False

  if is_administrator(ctx):
    return True

  if disnake.utils.get(ctx.author.roles, id=config.mod_role_id) is not None:
    return True
  return False

def get_cogs_in_folder():
  return [cog[:-3].lower() for cog in os.listdir("cogs") if str(cog).endswith(".py") and "__init__" not in str(cog)]

async def generate_error_message(ctx: commands.Context, text):
  return await ctx.send(embed=disnake.Embed(color=disnake.Color.dark_red(), title=":x: | Error", description=text), delete_after=config.error_duration)

async def generate_success_message(ctx: commands.Context, text):
  return await ctx.send(embed=disnake.Embed(color=disnake.Color.green(), title=":white_check_mark: | Success", description=text), delete_after=config.success_duration)

def split_to_parts(items: str, length: int):
  result = []

  for x in range(math.ceil(len(items) / length)):
    result.append(items[x * length:(x * length) + length])

  return result

async def delete_message(bot: commands.Bot, cnt: Union[commands.Context, disnake.Message, disnake.CommandInteraction]):
  if isinstance(cnt, disnake.CommandInteraction):
    return

  if isinstance(cnt, commands.Context):
    if cnt.guild is not None or cnt.message.author.id == bot.user.id:
      await cnt.message.delete()
  else:
    if cnt.guild is not None or cnt.message.author.id == bot.user.id:
      await cnt.delete()

# https://github.com/Toaster192/rubbergod/blob/master/utils.py
def get_command_group_signature(ctx: commands.Context):
  """Return signature of group command with checks
  `?group [subcommand1, subcommand2]`
  """
  subcommands = []
  if ctx.command.usage is not None:
    subcommands.append(ctx.command.signature)
  for subcommand in ctx.command.commands:
    for check in subcommand.checks:
      try:
        if not check(ctx):
          break
      except Exception:
        break
    else:
      subcommands.append(subcommand.name)

  group_string = f"{ctx.command.name} [{', '.join(subcommands)}]".rstrip(" ")
  return f"`{group_string}`"


# https://github.com/Toaster192/rubbergod/blob/master/utils.py
def get_command_signature(cmd_src: Union[commands.Context, commands.Command]):
  cmd = cmd_src.command if isinstance(cmd_src, commands.Context) else cmd_src
  cmd_string = f"{cmd} {cmd.signature}".rstrip(" ")
  return f"`{cmd_string}`"

def add_author_footer(embed: disnake.Embed, author: Union[disnake.User, disnake.Member],
                      set_timestamp=True, additional_text: Union[Iterable[str], None] = None):
  if set_timestamp:
    embed.timestamp = datetime.now(tz=timezone.utc)

  if additional_text is not None:
    embed.set_footer(icon_url=author.display_avatar.url, text=' | '.join((str(author), *additional_text)))
  else:
    embed.set_footer(icon_url=author.display_avatar.url, text=str(author))

  return embed
