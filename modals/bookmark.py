import disnake
from views.bookmark import BookmarkView
from features import bookmark


class BookmarkModal(disnake.ui.Modal):
    def __init__(self, message) -> None:
        self.message = message
        components = [
            disnake.ui.TextInput(
                label="Bookmark name",
                placeholder="Bookmark name",
                custom_id="name",
                style=disnake.TextInputStyle.short,
                required=True,
                max_length=100,
            ),
        ]
        super().__init__(title="Bookmark", custom_id="bookmark_tag", timeout=300, components=components)

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        embed, images, files_attached = await bookmark.create_bookmark_embed(self.message, inter.text_values["name"])

        try:
            if images:
                for image in images:
                    embed.append(bookmark.create_image_embed(self.message, image, inter.text_values["name"]))
            await inter.author.send(embeds=embed, view=BookmarkView(), files=files_attached)
            await inter.response.send_message(f"Bookmark **{inter.text_values['name']}** created", ephemeral=True)
        except disnake.HTTPException:
            return