import disnake

from util import general_util
from database import questions_and_answers_repo
from static_data.strings import Strings

class CreateQuestionAndAnswer(disnake.ui.Modal):
  def __init__(self):
    components = [
      disnake.ui.TextInput(label="Question", custom_id="q_and_a:question", required=True, max_length=3000, placeholder="Place here your question", style=disnake.TextInputStyle.multi_line),
      disnake.ui.TextInput(label="Answer", custom_id="q_and_a:answer", required=True, max_length=3000, placeholder="Place here your answer", style=disnake.TextInputStyle.multi_line)
    ]
    super(CreateQuestionAndAnswer, self).__init__(title="Create Question and Answer", custom_id="q_and_a_create", timeout=300, components=components)

  async def callback(self, interaction: disnake.ModalInteraction) -> None:
    if questions_and_answers_repo.create_question_and_answer(interaction.text_values["q_and_a:question"], interaction.text_values["q_and_a:answer"]) is None:
      return await general_util.generate_error_message(interaction, Strings.questions_and_answers_add_failed)
    await general_util.generate_success_message(interaction, Strings.questions_and_answers_add_added)
