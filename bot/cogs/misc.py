from os import name
from discord.ext.commands import Cog
from discord.ext.commands.context import Context
from discord.ext.commands.core import command
from requests_html import AsyncHTMLSession


class Cmds(Cog):
    def __init__(self, bot) -> None:
        bot.remove_command('help')
        self.bot = bot

    @command()
    async def p6(self, ctx: Context):
        await ctx.send(
            "```\nThe Neural Networks from Scratch video series will resume when the NNFS book is completed."
            " This means the videos will resume around Sept or Oct 2020.\n\nIf you are itching for the content,"
            " you can buy the book and get access to the draft now. The draft is over 500 pages,"
            " covering forward pass, activation functions, loss calcs, backward pass, optimization,"
            " train/test/validation for classification and regression. You can pre-order the book and get"
            " access to the draft via https://nnfs.io```")

    @command()
    async def search(self, ctx: Context, query: str):
        qsearch = query.replace(" ","%20")
        full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
        session = AsyncHTMLSession()
        r = await session.get(full_link)

        specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if "collection-item" in tut.html]

        if len(specific_tutorials) > 0:
            return_str = "\n---------------------------------------\n".join(f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
            return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

            await ctx.send(return_str)
        else:
            await ctx.send(
                f"```py\nTraceback (most recent call last):\n  File \"<stdin>\", line 1, in <module>\nNotFoundError: {query} not found```")

    @command(name="help")
    async def _help(self, ctx: Context, text: str):
        if text.lower() in {"sb", "sentdebot"}:
            await ctx.send(self.bot.cmds)

def setup(bot):
    bot.add_cog(Cmds(bot))
