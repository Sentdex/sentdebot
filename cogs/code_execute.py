import asyncio
import disnake
from disnake.ext import commands
import re
import requests
from typing import Union, Optional

from util import general_util
from config import cooldowns
from static_data.strings import Strings
from features.base_cog import Base_Cog

language_regex = re.compile(r"([\w\s\d]+)*```(\w*)([\s\S]*)```$")

class Code_Execute(Base_Cog):
  def __init__(self, bot:commands.Bot):
    super(Code_Execute, self).__init__(bot, __file__)

  @staticmethod
  def _run_code(lang: str, code: str, codeblock_args: Optional[list]):
    if codeblock_args is None:
      codeblock_args = []
    result = requests.post("https://emkc.org/api/v1/piston/execute", json={"language": lang, "source": code, "args": codeblock_args})
    if result.status_code != 200: return None
    return result.json()

  @commands.command(brief=Strings.code_execute_run_brief, help=Strings.code_execute_run_help, aliases=["r"])
  @cooldowns.default_cooldown
  async def run(self, ctx: commands.Context, *, codeblock: Optional[str]=None):
    message:disnake.Message = ctx.message
    if codeblock is None and message.reference is not None:
      channel:Union[disnake.TextChannel, None] = self.bot.get_channel(message.reference.channel_id)
      if channel is None:
        return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_reference_channel)

      message = await channel.fetch_message(message.reference.message_id)
      if message is None:
        return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_reference_message)

      codeblock = message.content

    await self.run_the_code(ctx, codeblock)

  @commands.message_command(name="Run Code")
  @cooldowns.default_cooldown
  async def run_code_message_command(self, inter: disnake.MessageCommandInteraction, message: disnake.Message):
    await self.run_the_code(inter, message.content)

  async def run_the_code(self, ctx, sourcecode: str):
    matches = language_regex.findall(sourcecode)

    if not matches:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_code_block)

    lang = matches[0][-2]
    codeblock_args = [arg for arg in matches[0][:-2][0].split("\n") if arg != ""]
    if not lang:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_cant_find_language_in_code_block)

    code: str = matches[0][-1]
    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(None, self._run_code, lang, code, codeblock_args)
    if result is None:
      return await general_util.generate_error_message(ctx, Strings.code_execute_run_failed_to_get_api_response)

    await self._send_result(ctx, result)

  @staticmethod
  async def _send_result(ctx: commands.Context, result: dict):
    if "message" in result:
      # There is error in code execution
      return await general_util.generate_error_message(ctx, general_util.truncate_string(result["message"], 4000, from_beginning=True))

    output = result["output"]
    output = general_util.truncate_string(output, 4000, from_beginning=True)

    embed = disnake.Embed(title=f"Ran your {result['language']} code", description=output, color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)

    await ctx.send(embed=embed)

def setup(bot):
  bot.add_cog(Code_Execute(bot))
