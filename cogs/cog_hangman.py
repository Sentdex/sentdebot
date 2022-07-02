"""Cog to play a game of hangman with the bot.
intended to be used as a learning module to understand how interacting with the discord/nextcord api works"""

from nextcord.ext import commands


class Hangman(commands.Cog, name="Hangman"):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(name="hangman", help="Play a game of hangman with the bot.")
    async def hangman(self, ctx):
        await ctx.send("This is the Hangman cog. It is currently in development.")
        await ctx.send("Please contact the developer if you have any questions.")


def setup(bot):
    bot.add_cog(Hangman(bot))