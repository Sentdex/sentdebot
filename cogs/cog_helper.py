"""Cog to handle various kinds of help messages that are not cog specific"""
from nextcord.ext import commands


class CogHelper(commands.Cog, name="Helper"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="get_help", help="Get help on a command", aliases=["help_command"])
    async def help(self, ctx, *, command: str):
        """Get help on a command"""
        try:
            await ctx.send(f"```{self.bot.get_command(command).help}```")
        except commands.CommandNotFound:
            await ctx.send(f"Command {command} not found")

    @commands.command(name="commands", help="Get help on all commands", aliases=["get_commands", "list_commands"])
    async def help_all(self, ctx):
        out = ""
        for command in self.bot.commands:
            if command.hidden:
                continue
            out += f"{command.name} - {command.help}\n"
        await ctx.send(f"```{out}```")



def setup(bot):
    bot.add_cog(CogHelper(bot))
