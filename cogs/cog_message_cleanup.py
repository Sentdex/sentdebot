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
        for channel in guild.text_channels:
            await channel.purge(limit=100, check=lambda m: m.author.bot or m.content.startswith(bot_config.prefix))

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith(self.bot.command_prefix):
            # flag message for delete, delay, 5 minutes
            await message.delete(delay=5)


def setup(bot):
    bot.add_cog(MessageCleanup(bot))
