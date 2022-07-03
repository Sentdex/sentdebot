"""cog to enable polling, voting, and other features"""
import nextcord
from nextcord.ext import commands, tasks


class Voter(commands.Cog, name="Democracy Cog"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='vote', help='create a vote', usage='"Question" option1 option2 option3')
    async def vote(self, ctx, question, *options):

        if len(options) < 2:
            await ctx.send('You need at least 2 options to create a vote')
            return
        elif len(options) > 10:
            await ctx.send('You can only have 10 options')
            return
        else:
            emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
            # we need to arrange as an embed to send to the channel, and then we need to add a reaction for each option
            embed = nextcord.Embed(title=question, color=0x00ff00)
            for i in range(len(options)):
                embed.add_field(name=options[i] + ':', value=emoji_list[i])
            out = await ctx.send('Vote:', embed=embed)
            for i in range(len(options)):
                # add reaction to embed
                await out.add_reaction(emoji_list[i])
            # make out a thread
            thread = await out.create_thread(name=f"{question} Discussion Thread")
            # ping @here in thread
            try:
                await thread.send(f"@here")
            except nextcord.HTTPException:
                pass


def setup(bot):
    bot.add_cog(Voter(bot))

