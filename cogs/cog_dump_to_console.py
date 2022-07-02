"""Cog that dumps chat to console"""
import nextcord
from nextcord.ext import commands

class CogDumpToConsole(commands.Cog, name="Dump To Console"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        print(f"{message.created_at} {message.author.name} {message.content}")
        await self.bot.process_commands(message)

def setup(bot):
    bot.add_cog(CogDumpToConsole(bot))