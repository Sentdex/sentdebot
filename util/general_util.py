# Store for essential functions

import math
import disnake
from disnake.ext import commands
from typing import Union, Iterable, List, Tuple
import os
from datetime import datetime, timezone

from config import config

def is_administrator(ctx):
  if ctx.bot.owner_id == ctx.author.id:
    return True

  if not isinstance(ctx.author, disnake.Member):
    return False

  if ctx.author.id == ctx.guild.owner_id:
    return True

  for role_id in config.ids.admin_role:
    if disnake.utils.get(ctx.author.roles, id=role_id) is not None:
      return True
  return False

def is_mod(ctx):
  if ctx.bot.owner_id == ctx.author.id:
    return True

  if not isinstance(ctx.author, disnake.Member):
    return False

  if ctx.author.id == ctx.guild.owner_id:
    return True

  if is_administrator(ctx):
    return True

  for role_id in config.ids.mod_role:
    if disnake.utils.get(ctx.author.roles, id=role_id) is not None:
      return True
  return False

def get_cogs_in_folder():
  return [cog[:-3].lower() for cog in os.listdir("cogs") if str(cog).endswith(".py") and "__init__" not in str(cog)]

async def generate_error_message(ctx: Union[commands.Context, disnake.Message, disnake.MessageInteraction, disnake.ModalInteraction, disnake.CommandInteraction], text):
  response_embed = disnake.Embed(color=disnake.Color.dark_red(), title=":x: | Error", description=text)
  if isinstance(ctx, disnake.ModalInteraction) or isinstance(ctx, disnake.CommandInteraction) or isinstance(ctx, disnake.MessageInteraction):
    return await ctx.send(embed=response_embed, ephemeral=True)
  elif isinstance(ctx, disnake.Message):
    return await ctx.reply(embed=response_embed)
  else:
    return await ctx.send(embed=response_embed, delete_after=config.base.error_duration)

async def generate_success_message(ctx: Union[commands.Context, disnake.Message, disnake.MessageInteraction, disnake.ModalInteraction, disnake.CommandInteraction], text):
  response_embed = disnake.Embed(color=disnake.Color.green(), title=":white_check_mark: | Success", description=text)
  if isinstance(ctx, disnake.ModalInteraction) or isinstance(ctx, disnake.CommandInteraction) or isinstance(ctx, disnake.MessageInteraction):
    return await ctx.send(embed=response_embed, ephemeral=True)
  elif isinstance(ctx, disnake.Message):
    return await ctx.reply(embed=response_embed)
  else:
    return await ctx.send(embed=response_embed, delete_after=config.base.success_duration)

def split_to_parts(items: str, length: int):
  result = []

  for x in range(math.ceil(len(items) / length)):
    result.append(items[x * length:(x * length) + length])

  return result

async def delete_message(bot: commands.Bot, cnt: Union[commands.Context, disnake.Message, disnake.CommandInteraction]):
  if isinstance(cnt, disnake.CommandInteraction):
    return

  try:
    if isinstance(cnt, commands.Context):
      if cnt.guild is not None or cnt.message.author.id == bot.user.id:
        await cnt.message.delete()
    else:
      if cnt.guild is not None or cnt.message.author.id == bot.user.id:
        await cnt.delete()
  except:
    pass


# https://github.com/Toaster192/rubbergod/blob/master/utils.py
def get_command_signature(cmd_src: Union[commands.Context, commands.Command]):
  cmd = cmd_src.command if isinstance(cmd_src, commands.Context) else cmd_src
  cmd_string = f"{cmd}({','.join(cmd.signature.split(' '))})".rstrip(" ")
  return f"{cmd_string}"

def add_author_footer(embed: disnake.Embed, author: Union[disnake.User, disnake.Member],
                      set_timestamp=True, additional_text: Union[Iterable[str], None] = None):
  if set_timestamp:
    embed.timestamp = datetime.now(tz=timezone.utc)

  if additional_text is not None:
    embed.set_footer(icon_url=author.display_avatar.url, text=' | '.join((str(author), *additional_text)))
  else:
    embed.set_footer(icon_url=author.display_avatar.url, text=str(author))

  return embed

def add_string_until_length(strings:List[str], max_length:int, sep:str) -> Tuple[str, List[str]]:
  output = ""
  number_of_strings = len(strings)
  for _ in range(number_of_strings):
    string = strings.pop(0)
    tmp_output = (output + string) if output == "" else (output + sep + string)
    if len(tmp_output) > max_length:
      break
    output = tmp_output
  return output, strings

def truncate_string(string: str, limit: int=12, ellipsis :str="…") -> str:
  return string[:limit - len(ellipsis)] + ellipsis if len(string) > limit else string

def get_user_stats(guild):
  members = guild.members

  online, idle, offline = 0, 0, 0
  for member in members:
    if member.status == disnake.Status.online:
      online += 1
    elif member.status == disnake.Status.offline:
      offline += 1
    else:
      idle += 1

  return online, idle, offline
