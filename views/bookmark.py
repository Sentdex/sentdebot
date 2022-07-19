import disnake


class BookmarkView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(disnake.ui.Button(label="Delete bookmark", style=disnake.ButtonStyle.danger, custom_id="bookmark:delete"))

    async def interaction_check(self, interaction: disnake.MessageInteraction) -> None:
        if interaction.data.custom_id == "bookmark:delete":
            try:
                await interaction.message.delete()
            except:
                pass