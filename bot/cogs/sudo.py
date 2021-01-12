import logging
import traceback

from discord.ext.commands import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command
from discord.ext.commands.errors import CheckFailure, CommandError

from .utils import is_user


class Sudo(Cog):
    logger = logging.getLogger(f"<Cog 'Sudo' at {__name__}>")

    def __init__(self, bot) -> None:
        self.bot = bot
        self.gen_chat = self.bot.guild.get_channel(self.bot.channels[0])

    # Sentdex Only (i don't know for sure whether he owns the bot)
    @command(aliases=["gtfo"])
    @is_user(324953561416859658)
    async def logout(self, ctx: Context):
        await ctx.bot.logout()

    @command()
    @is_user(324953561416859658)
    async def get_history(self, ctx):
        async for message in self.gen_chat.history(limit=999999999999999):
            if message.author.id == 324953561416859658:
                with open(self.bot.path / "history_out.csv", "a") as f:
                    f.write(f"{message.created_at},1\n")

    async def cog_command_error(self, ctx: Context, error: CommandError):
        if isinstance(error, CheckFailure):
            await ctx.send("You are not privileged enough to use this command", delete_after=5.0)
        else:
            self.logger.error(f"In {ctx.command.qualified_name}:")
            traceback.print_tb(error.original.__traceback__)
            self.logger.error(
                f"{error.original.__class__.__name__}: {error.original}")

def setup(bot):
    bot.add_cog(Sudo(bot))
