import time

import discord
from discord.ext import commands

from bot_config import BotConfig
from bot_definitions import get_all_channels_by_tag

bot_config = BotConfig.get_config('sentdebot')


class MessageCleanup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ignored_channels = [c.id for c in get_all_channels_by_tag('no-cleanup')]

    # on startup, clean up messages
    @commands.Cog.listener()
    async def on_ready(self):
        # sweep on startup
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(bot_config.guild_id)
        # only delete if it THIS bot
        for channel in guild.text_channels:
            if channel.id not in self.ignored_channels:
                async for message in channel.history(limit=None, oldest_first=True):
                    if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
                        if time.time() - message.created_at.timestamp() > 86400:
                            await message.delete()

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
            # if not channel is in ignored list
            if message.channel.id not in self.ignored_channels:
                await message.delete(delay=86400)

    # sweep command
    @commands.command(name='sweep()')
    @commands.has_permissions(manage_messages=True)
    async def sweep(self, ctx):
        guild = self.bot.get_guild(bot_config.guild_id)
        # only delete if it THIS bot
        for channel in guild.text_channels:
            async for message in channel.history(limit=None, oldest_first=True):
                if message.author == self.bot.user or message.content.startswith(self.bot.command_prefix):
                    if time.time() - message.created_at.timestamp() > 86400:
                        await message.delete()
        await ctx.send('Sweeped!')



def setup(bot):
    bot.add_cog(MessageCleanup(bot))
