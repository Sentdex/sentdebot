import disnake
from typing import List, Optional, Union

from util import general_util

reaction_ids = ["vote:zero", "vote:one", "vote:two", "vote:three", "vote:four", "vote:six", "vote:seven", "vote:eight", "vote:nine"]
reactions = ["0️⃣", "1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
reaction_buttons = [disnake.ui.Button(emoji=f"{reactions[i]}", custom_id=rid,style=disnake.ButtonStyle.primary) for i, rid in enumerate(reaction_ids)]

class VoteView(disnake.ui.View):
  def __init__(self, description: str, choices: List[str], timeout: Optional[float]=300, color: disnake.Color=disnake.Color.dark_blue()):
    super(VoteView, self).__init__(timeout=timeout)

    self.message: Optional[Union[disnake.Message, disnake.ApplicationCommandInteraction, disnake.ModalInteraction, disnake.MessageCommandInteraction]] = None
    self.choices = choices
    self.description = description
    self.color = color

    self.number_of_choices = min(len(choices), 10)
    self.results = [0 for _ in range(self.number_of_choices)]
    self.participants = []

    for i in range(self.number_of_choices):
      self.add_item(reaction_buttons[i])

  async def run(self, ctx):
    if self.number_of_choices == 0:
      return None

    embed = disnake.Embed(title="Vote", description=general_util.truncate_string(self.description, 4000), color=self.color)
    for idx, (reaction_id, choice) in enumerate(zip(reaction_ids, self.choices)):
      embed.add_field(name=f"{reactions[idx]}", value=general_util.truncate_string(choice, 1000))
    general_util.add_author_footer(embed, ctx.author)

    message = await ctx.send(embed=embed, view=self)
    if isinstance(ctx, (disnake.ApplicationCommandInteraction, disnake.ModalInteraction, disnake.MessageCommandInteraction)):
      self.message = ctx
    else:
      self.message = message

  async def interaction_check(self, interaction: disnake.MessageInteraction) -> None:
    if interaction.author.id in self.participants:
      return await general_util.generate_error_message(interaction, "You already participated in this pool")

    self.participants.append(interaction.author.id)

    if interaction.data.custom_id not in reaction_ids:
      self.participants.remove(interaction.author.id)
      return

    try:
      inter_index = reaction_ids.index(interaction.data.custom_id)
    except:
      self.participants.remove(interaction.author.id)
      return

    self.results[inter_index] += 1
    await general_util.generate_success_message(interaction, f"You voted for choice {reactions[inter_index]}\n`{self.choices[inter_index]}`")

  async def stop(self) -> None:
    super(VoteView, self).stop()
    await self.on_timeout()

  async def on_timeout(self):
    if isinstance(self.message, disnake.Message):
      message = self.message
    else:
      message = await self.message.original_message()

    try:
      self.clear_items()
      await message.edit(view=self)
    except:
      pass

    max_res = max(self.results)

    if max_res == 0:
      embed = disnake.Embed(title="Vote results", description=f"There is no winner", color=disnake.Color.orange())
    else:
      res_indexes = []
      for idx, result in enumerate(self.results):
        if result == max_res:
          res_indexes.append(idx)

      res_reactions = [reaction for idx, reaction in enumerate(reactions) if idx in res_indexes]
      res_choices, _ = general_util.add_string_until_length([choice for idx, choice in enumerate(self.choices) if idx in res_indexes], 3000, "\n")
      embed = disnake.Embed(title="Vote results", description=f"{', '.join(res_reactions)} {'choice' if len(res_indexes) == 1 else 'choices'} won:\n`{res_choices}`\n[Link]({message.jump_url})", color=self.color)

    try:
      await message.reply(embed=embed)
    except:
      pass
