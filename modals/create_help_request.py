import disnake

class HelpRequestModal(disnake.ui.Modal):
  def __init__(self, data_callback):
    components = [
      disnake.ui.TextInput(label="Title", custom_id="help_request:title", required=True, max_length=90, placeholder="Short title"),
      disnake.ui.TextInput(label="Tags", custom_id="help_request:tags", required=False, max_length=90, placeholder="python;tensorflow;classifier"),
      disnake.ui.TextInput(label="Description", custom_id="help_request:description", required=True, placeholder="Here describe your problem", style=disnake.TextInputStyle.multi_line)
    ]
    super(HelpRequestModal, self).__init__(title="Help request creation", custom_id="help_request", timeout=300, components=components)

    self.data_callback = data_callback

  async def callback(self, interaction: disnake.ModalInteraction) -> None:
    await self.data_callback(interaction, interaction.text_values)

