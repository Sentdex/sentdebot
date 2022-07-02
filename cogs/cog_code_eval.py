"""A pyston rest api powered code evaluator"""
from nextcord.ext import commands
from pyston import PystonClient, File

class CodeEval(commands.Cog, name="Code Evaluator"):

    @commands.command(name='eval', help='Evaluates code')
    async def eval(self, ctx, *, code):
        """Evaluates code
        Usage example:
        'bot_prefix eval
        ```python
        print("Hello World")
        ```
        """
        try:
            client = PystonClient()  # new client for each eval so no pollution
            lang, code = map(str.strip, code.strip('"\'`\n').split('\n', 1))
            if len(code) > 265:
                # tell user code is too long
                await ctx.send(f"""```py
            Traceback (most recent call last):
                File "<stdin>", line 1, in <module>
            SyntaxError: {code} is too long```""")
                return

            output = await client.execute(lang, [File(code)])

            await ctx.send(f"```py\n{output}\n```")
        except Exception as e:
            print(e)
            await ctx.send(
                f"""```py
        Traceback (most recent call last):
            File "<stdin>", line 1, in <module>
        {e}```"""
            )


def setup(bot):
    bot.add_cog(CodeEval())
