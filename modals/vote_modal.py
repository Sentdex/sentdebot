import asyncio

import disnake

from features.vote_prompt import VoteView
from config import config

class VoteSetupModal(disnake.ui.Modal):
  def __init__(self):
    components = [
      disnake.ui.TextInput(label="Description", custom_id="vote_setup:description", required=False, max_length=3000, placeholder="Optional description", style=disnake.TextInputStyle.multi_line),
      disnake.ui.TextInput(label="Choice 1", custom_id="vote_setup:choice_1", required=True, max_length=300, placeholder="Required choice 1"),
      disnake.ui.TextInput(label="Choice 2", custom_id="vote_setup:choice_2", required=True, max_length=300, placeholder="Required choice 2"),
      disnake.ui.TextInput(label="Choice 3", custom_id="vote_setup:choice_3", required=False, max_length=300, placeholder="Optional choice 3"),
      disnake.ui.TextInput(label="Choice 4", custom_id="vote_setup:choice_4", required=False, max_length=300, placeholder="Optional choice 4")
    ]
    super(VoteSetupModal, self).__init__(title="Setup Vote", custom_id="vote_setup", timeout=300, components=components)

  async def callback(self, interaction: disnake.ModalInteraction) -> None:
    choices = [choice for (key, choice) in dict(interaction.text_values).items() if "choice" in key and choice != ""]
    vote_prompt = VoteView(description=interaction.text_values["vote_setup:description"], choices=choices, timeout=None)
    await vote_prompt.run(interaction)
    await asyncio.sleep(config.common.vote_duration_seconds)
    await vote_prompt.stop()
