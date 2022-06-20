from discord.ext import commands


# a search query
from requests_html import HTMLSession


class SearchTools(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search', help='search for a string', args=['QUERY'])
    async def search(self, ctx, *, query):
        print(query)

        qsearch = query.replace(" ", "%20")
        full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
        print(full_link)
        session = HTMLSession()
        r = session.get(full_link)

        specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if
                              "collection-item" in tut.html]

        if len(specific_tutorials) > 0:
            return_str = "\n---------------------------------------\n".join(
                f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
            return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

            await ctx.send(return_str)
        else:
            await ctx.send(f"""```py
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        NotFoundError: {query} not found```""")


    # function to serach sentdex' youtube channel for a video, send a list of results to the channel
    @commands.command(name='search_youtube()', help='search for a video on youtube', args=['QUERY'], aliases=['search_youtube'])
    async def search_youtube(self, ctx, query):
        await ctx.send('This command is not implemented yet')

    # function to search


def setup(bot):
    bot.add_cog(SearchTools(bot))
