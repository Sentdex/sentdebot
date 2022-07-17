import asyncio
import disnake as discord
from disnake.ext import commands
import re
import requests
from typing import Union

from util import general_util
from config import cooldowns
from static_data.strings import Strings
from features.base_cog import Base_Cog

language_regex = re.compile(r"(\w*)\s*```(\w*)?([\s\S]*)```$")

class Code_Execute(Base_Cog):
  def __init__(self, bot:commands.Bot):
    super(Code_Execute, self).__init__(bot, __file__)

  @staticmethod
  def _run_code(lang: str, code: str):
    result = requests.post("https://emkc.org/api/v1/piston/execute", json={"language": lang, "source": code})
    if result.status_code != 200: return None
    return result.json()

  @commands.command(brief=Strings.code_execute_run_brief, help=Strings.code_execute_run_help, aliases=["r"])
  @cooldowns.default_cooldown
  async def run(self, ctx: commands.Context, *, codeblock: str=None):
    message:discord.Message = ctx.message
    if codeblock is None and message.reference is not None:
      channel:Union[discord.TextChannel, None] = self.bot.get_channel(message.reference.channel_id)
      if channel is None:
        return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_reference_channel)

      message = await channel.fetch_message(message.reference.message_id)
      if message is None:
        return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_reference_message)

      codeblock = message.content

    matches = language_regex.findall(codeblock)

    if not matches:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_code_block)

    lang = matches[0][0] or matches[0][1]
    if not lang:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_language_in_code_block)

    code:str = matches[0][2]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self._run_code, lang, code)
    if result is None:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_failed_to_get_api_response)

    await self._send_result(ctx, result, code.rstrip("\n").lstrip("\n"))

  @staticmethod
  async def _send_result(ctx: commands.Context, result: dict, src:str):
    if "message" in result:
      # There is error in code execution
      return await general_util.generate_error_message(ctx, result["message"])

    output = result["output"]
    output = general_util.split_to_parts(output, 1000)
    desc = ("**Output shortened**\n" if len(output) > 1 else "") + f"*{src}*"

    embed = discord.Embed(title=f"Ran your {result['language']} code", color=discord.Color.green(), description=desc)
    embed.add_field(name="Output", value=output[-1])
    general_util.add_author_footer(embed, ctx.author)

    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Code_Execute(bot))
