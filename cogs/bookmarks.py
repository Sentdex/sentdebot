import disnake
from disnake.ext import commands

from features.base_cog import Base_Cog
from views.bookmark import BookmarkView
from features import bookmark
from modals.bookmark import BookmarkModal
from features.reaction_context import ReactionContext

class Bookmarks(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Bookmarks, self).__init__(bot, __name__)

  async def handle_reaction_add(self, ctx: ReactionContext):
    if ctx.author is None:
      return

    if str(ctx.emoji) == "🔖":
      embed, images, files_attached = await bookmark.create_bookmark_embed(ctx.message, "Bookmark")
      try:
        if images:
          for image in images:
            embed.append(bookmark.create_image_embed(ctx.message, image, "Image"))
        await ctx.author.send(embeds=embed, view=BookmarkView(), files=files_attached)
      except disnake.HTTPException:
        return

  @commands.message_command(name="Bookmark")
  async def bookmark(self, inter: disnake.MessageCommandInteraction, message: disnake.Message):
    await inter.response.send_modal(modal=BookmarkModal(message))

def setup(bot):
  bot.add_cog(Bookmarks(bot))
