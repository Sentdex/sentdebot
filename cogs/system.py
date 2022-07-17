# Administration extension

import disnake
from disnake.ext import commands
import asyncio
import math
from typing import Optional

from config import config
from features.base_cog import Base_Cog
from util import general_util
from util.logger import setup_custom_logger
from static_data.strings import Strings
from features.paginator import EmbedView

logger = setup_custom_logger(__name__)

global_bot_reference: Optional[commands.Bot] = None


async def unloaded_cogs_autocomplete(_, search: str):
  loaded_cogs = [str(cog.file) for cog in global_bot_reference.cogs.values()]
  all_cogs = general_util.get_cogs_in_folder()

  unloaded_cogs = [cog for cog in all_cogs if cog not in loaded_cogs]

  if search is None or search == "":
    unloaded_cogs.append("all")
    return unloaded_cogs

  ret = [cog for cog in unloaded_cogs if search.lower() in cog.lower()]
  ret.append("all")
  return ret


async def loaded_cogs_autocomplete(_, search: str):
  loaded_cogs = [str(cog.file) for cog in global_bot_reference.cogs.values()]

  if search is None or search == "":
    loaded_cogs.append("all")
    return loaded_cogs

  ret = [cog for cog in loaded_cogs if search.lower() in cog.lower()]
  ret.append("all")
  return ret


async def loaded_cogs_not_protected_autocomplete(_, search: str):
  loaded_cogs = [str(cog.file) for cog in global_bot_reference.cogs.values() if str(cog.file) not in config.protected_cogs]

  if search is None or search == "":
    loaded_cogs.append("all")
    return loaded_cogs

  ret = [cog for cog in loaded_cogs if search.lower() in cog.lower()]
  ret.append("all")
  return ret

class System(Base_Cog):
  def __init__(self, bot: commands.Bot):
    global global_bot_reference
    global_bot_reference = bot
    super(System, self).__init__(bot, __file__)

  @commands.slash_command(name="extensions")
  async def extensions(self, inter: disnake.CommandInteraction):
    pass

  @extensions.sub_command(name="load", description=Strings.system_load_brief)
  @commands.check(general_util.is_administrator)
  @commands.guild_only()
  async def load(self, inter: disnake.CommandInteraction, extension_name: str=commands.Param(autocomplete=unloaded_cogs_autocomplete, description="Name of extension to load")):
    if extension_name.lower() == "all":
      final_embed = disnake.Embed(title="Extensions loaded", color=disnake.Color.green(), description="Failed extensions:")

      loaded_cogs = [cog.file for cog in self.bot.cogs.values()]
      cogs_in_folder = general_util.get_cogs_in_folder()

      for cog in cogs_in_folder:
        if str(cog) not in loaded_cogs:
          try:
            self.bot.load_extension(f"cogs.{str(cog)}")
            logger.info(f"{str(cog)} loaded")
            await asyncio.sleep(0)
          except Exception as e:
            final_embed.description += f"\n{str(cog)}"
            final_embed.colour = disnake.Color.orange()

            await general_util.generate_error_message(inter, Strings.system_unable_to_load_cog(cog=str(cog), e=e))

      await inter.send(embed=final_embed, ephemeral=True)
    else:
      try:
        self.bot.load_extension(f"cogs.{extension_name}")
        logger.info(f"{extension_name} loaded")

        await general_util.generate_success_message(inter, Strings.system_cog_loaded(extension=extension_name))
      except Exception as e:
        await general_util.generate_error_message(inter, Strings.system_unable_to_load_cog(cog=extension_name, e=e))

  @extensions.sub_command(name="unload", description=Strings.system_unload_brief)
  @commands.check(general_util.is_administrator)
  @commands.guild_only()
  async def unload(self, inter: disnake.CommandInteraction, extension_name: str=commands.Param(autocomplete=loaded_cogs_not_protected_autocomplete, description="Name of extension to unload")):
    if extension_name in config.protected_cogs:
      return await general_util.generate_error_message(inter, Strings.system_unload_protected_cog(extension=extension_name))

    if extension_name.lower() == "all":
      final_embed = disnake.Embed(title="Extensions unload", color=disnake.Color.green(), description="Failed extensions:")

      loaded_cogs = [cog.file for cog in self.bot.cogs.values()]

      for cog in loaded_cogs:
        if cog not in config.protected_cogs:
          try:
            self.bot.unload_extension(f"cogs.{cog}")
            logger.info(f'{cog} unloaded')
            await asyncio.sleep(0)
          except Exception as e:
            final_embed.description += f"\n{str(cog)}"
            final_embed.colour = disnake.Color.orange()

            await general_util.generate_error_message(inter, Strings.system_unable_to_unload_cog(cog=cog, e=e))

      await inter.send(embed=final_embed, ephemeral=True)
    else:
      try:
        self.bot.unload_extension(f"cogs.{extension_name}")
        logger.info(f'{extension_name} unloaded')
        await general_util.generate_success_message(inter, Strings.system_cog_unloaded(extension=extension_name))
      except Exception as e:
        await general_util.generate_error_message(inter, Strings.system_unable_to_unload_cog(cog=extension_name, e=e))

  @extensions.sub_command(name="reload", description=Strings.system_reload_brief)
  @commands.check(general_util.is_administrator)
  @commands.guild_only()
  async def reload(self, inter: disnake.CommandInteraction, extension_name: str=commands.Param(autocomplete=loaded_cogs_autocomplete, description="Name of extension to reload")):
    loaded_cogs = [cog.file for cog in self.bot.cogs.values()]

    if extension_name.lower() == "all":
      final_embed = disnake.Embed(title="Extensions reloaded", color=disnake.Color.green(), description="Failed extensions:")

      for cog in loaded_cogs:
        try:
          self.bot.reload_extension(f"cogs.{cog}")
          logger.info(f"{cog} reloaded")
          await asyncio.sleep(0)
        except Exception as e:
          final_embed.description += f"\n{str(cog)}"
          final_embed.colour = disnake.Color.orange()

          await general_util.generate_error_message(inter, Strings.system_unable_to_reload_cog(cog=cog, e=e))

      await inter.send(embed=final_embed, ephemeral=True)
    else:
      try:
        self.bot.reload_extension(f"cogs.{extension_name}")
        logger.info(f"{extension_name} reloaded")

        await general_util.generate_success_message(inter, Strings.system_cog_reloaded(extension=extension_name))
      except Exception as e:
        await general_util.generate_error_message(inter, Strings.system_unable_to_reload_cog(cog=extension_name, e=e))

  @extensions.sub_command(name="list", description=Strings.system_cogs_brief)
  @commands.check(general_util.is_administrator)
  @commands.guild_only()
  async def cogs(self, inter: disnake.CommandInteraction):
    cogs_in_folder = general_util.get_cogs_in_folder()
    loaded_cogs = [cog.file for cog in self.bot.cogs.values()]

    number_of_batches = math.ceil(len(cogs_in_folder) / 21)
    cogs_in_folder_batches = [cogs_in_folder[i * 21: i * 21 + 21] for i in range(number_of_batches)]

    pages = []
    for batch in cogs_in_folder_batches:
      embed = disnake.Embed(title="Cogs", description="List of all loaded and unloaded cogs", color=disnake.Color.dark_magenta())

      for idx, cog in enumerate(batch):
        status = "🔒 *protected*" if cog in config.protected_cogs else ("✅ **loaded**" if cog in loaded_cogs else "❌ **unloaded**")
        embed.add_field(name=cog, value=status)

      pages.append(embed)

    await EmbedView(inter.author, pages, perma_lock=True).run(inter)

  @commands.command(brief=Strings.system_logout_brief, aliases=["gtfo"])
  @commands.check(general_util.is_administrator)
  @commands.guild_only()
  async def logout(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)
    await ctx.send("Cya :wave:")
    await self.bot.close()

def setup(bot):
  bot.add_cog(System(bot))
