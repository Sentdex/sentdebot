import discord
from discord.ext import commands

from bot_config import BotConfig

bot_config = BotConfig.get_config('sentdebot')

class ChannelCreator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name='make_structure()', help='emulate the sentdex discord structure')
    async def make_structure(self, ctx):
        for channel in bot_config.channels:
            if discord.utils.get(ctx.guild.channels, name=channel.name):
                # replace the bot_config.channels id with the discord channel id
                channel.id = discord.utils.get(ctx.guild.channels, name=channel.name).id
            else:
                if channel.channel_type == 'text':
                    await ctx.guild.create_text_channel(channel.name)
                if channel.channel_type == 'voice':
                    await ctx.guild.create_voice_channel(channel.name)
                channel.id = discord.utils.get(ctx.guild.channels, name=channel.name).id
        await ctx.send('Done!')

def setup(bot):
    bot.add_cog(ChannelCreator(bot))
    print('CommunityStats loaded')