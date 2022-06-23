"""cog to create and maintain a channel called toilet, that only holds a history of 10 messages, older ones get deleted.
For development purposes (bot spam etc.)"""
import nextcord as discord
from nextcord import NotFound
from nextcord.ext import commands, tasks


class ToiletChannel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            toilet_channel = discord.utils.get(guild.text_channels, name='__toilet__')
            if toilet_channel is None:
                await guild.create_text_channel('__toilet__')
            else:
                messages = await toilet_channel.history(limit=None, oldest_first=False).flatten()
                if len(messages) > 10:
                    for message in messages[10:]:
                        await message.delete()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.name == '__toilet__':
            history = await message.channel.history(limit=None, oldest_first=False).flatten()
            if len(history) > 10:
                for message in history[10:]:
                    try:
                        await message.delete()
                    except NotFound:
                        pass
                    except discord.Forbidden:
                        await message.channel.send(f'I do not have permission to delete messages in {message.channel.mention}')
                    except Exception as e:
                        await message.channel.send(f'Something went wrong while deleting messages in {message.channel.mention}')
                        raise e

def setup(bot):
    bot.add_cog(ToiletChannel(bot))
