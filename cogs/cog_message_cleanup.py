import time

import discord
from discord.ext import commands

from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')


class MessageCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # on startup, clean up messages
    @commands.Cog.listener()
    async def on_ready(self):
        # search for messaged that are older than 24 hour that are from the bot or start with the bot prefix
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(bot_config.guild_id)
        # only delete if it THIS bot
        for channel in guild.text_channels:
            async for message in channel.history(limit=None, oldest_first=True):
                if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
                    if time.time() - message.created_at.timestamp() > 60*5:
                        await message.delete()

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
            await message.delete(delay=300)


def setup(bot):
    bot.add_cog(MessageCleanup(bot))
