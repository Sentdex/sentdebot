import disnake
from disnake.ext import commands
from Levenshtein import ratio

from util import general_util
from database import questions_and_answers_repo
from config import config, cooldowns
from util.logger import setup_custom_logger
from features.base_cog import Base_Cog
from modals.question_and_answer import CreateQuestionAndAnswer
from features.paginator import EmbedView
from static_data.strings import Strings

logger = setup_custom_logger(__name__)

def getApproximateAnswer(q):
  max_score = 0
  answer_id = -1
  ref_question = None

  questions = questions_and_answers_repo.get_all_questions()

  for ans_id, question in questions:
    score = ratio(question, q)
    if score >= 0.9:
      return question, questions_and_answers_repo.get_answer_by_id(ans_id), score
    elif score > max_score:
      max_score = score
      answer_id = ans_id
      ref_question = question

  if (max_score * 100) > config.questions_and_answers.score_limit:
    return ref_question, questions_and_answers_repo.get_answer_by_id(answer_id), max_score
  return None, None, None

class QuestionsAndAnswers(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(QuestionsAndAnswers, self).__init__(bot, __file__)

  @commands.Cog.listener()
  async def on_message(self, message: disnake.Message):
    if message.guild is None: return
    if config.ids.main_guild != message.guild.id: return
    if message.author.bot: return
    if message.content == "" or message.content.startswith(config.base.command_prefix + "."): return

    channel = message.channel.parent if isinstance(message.channel, disnake.Thread) else message.channel
    if channel.id != config.ids.help_channel: return

    ref_question, answer, score = getApproximateAnswer(message.content)
    if answer is None: return

    logger.info(f"Found answer for users question: `{message.content}`\nReference question: `{ref_question}`\nAnswer: `{answer}`")

    await message.reply(Strings.questions_and_answers_repond_format(result=answer))

  @commands.slash_command(name="question_and_answer")
  async def question_and_answer(self, inter: disnake.CommandInteraction):
    pass

  @question_and_answer.sub_command(name="add", description=Strings.questions_and_answers_add_description)
  @commands.check(general_util.is_mod)
  async def add_question_and_answer(self, inter: disnake.CommandInteraction):
    await inter.response.send_modal(modal=CreateQuestionAndAnswer())

  @question_and_answer.sub_command(name="remove", description=Strings.questions_and_answers_remove_description)
  @commands.check(general_util.is_mod)
  async def add_question_and_answer(self, inter: disnake.CommandInteraction, question: str):
    questions_and_answers_repo.remove_question(question)
    await general_util.generate_success_message(inter, Strings.questions_and_answers_remove_removed)

  @question_and_answer.sub_command(name="list", description=Strings.questions_and_answers_list_description)
  @cooldowns.default_cooldown
  async def question_and_answer_list(self, inter: disnake.CommandInteraction):
    data = questions_and_answers_repo.get_all()

    question_answer_pairs = [f"**Question:** {question}\n**Answer:** {answer}\n" for question, answer in data]

    pages = []
    while question_answer_pairs:
      embed = disnake.Embed(title="Q&A List", color=disnake.Color.dark_blue())
      general_util.add_author_footer(embed, inter.author)
      output, question_answer_pairs = general_util.add_string_until_length(question_answer_pairs, 4000, "\n")
      embed.description = output.strip()
      pages.append(embed)

    if pages:
      await EmbedView(inter.author, pages).run(inter)
    else:
      embed = disnake.Embed(title="Q&A List", description="*No questions and answers available*", color=disnake.Color.dark_blue())
      general_util.add_author_footer(embed, inter.author)
      await inter.send(embed=embed, ephemeral=True)

def setup(bot):
  bot.add_cog(QuestionsAndAnswers(bot))
