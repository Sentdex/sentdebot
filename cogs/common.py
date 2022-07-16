import disnake
from disnake.ext import commands
from requests_html import HTMLSession

from config import cooldowns
from static_data.strings import Strings
from features.base_cog import Base_Cog
from util import general_util
from database import projects_repo

class Common(Base_Cog):
  def __init__(self, bot: commands.Bot):
    super(Common, self).__init__(bot, __file__)

  @commands.command(brief=Strings.common_member_count_brief)
  @cooldowns.default_cooldown
  @commands.guild_only()
  async def member_count(self, ctx: commands.Context):
    await general_util.delete_message(self.bot, ctx)
    await ctx.send(embed=disnake.Embed(title="Member count", description=f"{ctx.guild.member_count} :monkey:", color=disnake.Color.dark_blue()))

  @commands.command(brief=Strings.common_search_brief)
  @cooldowns.default_cooldown
  async def search(self, ctx: commands.Context, *, search_term: str):
    await general_util.delete_message(self.bot, ctx)

    search_term_cleared = search_term.replace(" ", "%20")
    search_link = f"https://pythonprogramming.net/search/?q={search_term_cleared}"

    session = HTMLSession()
    r = session.get(search_link)

    specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if "collection-item" in tut.html]

    if len(specific_tutorials) > 0:
      embed = disnake.Embed(title=f"Results for '{search_term[:150]}'", description=f"More results: <{search_link}>", color=disnake.Color.dark_blue())
      for result in specific_tutorials[:5]:
        embed.add_field(name=f"{result[0]}", value=f"<https://pythonprogramming.net{result[1]}>", inline=False)
      general_util.add_author_footer(embed, ctx.author)

      await ctx.send(embed=embed)
    else:
      await general_util.generate_error_message(ctx, Strings.populate_string("common_search_nothing_found", term=search_term))

  @commands.slash_command(name="projects")
  async def projects(self, inter: disnake.CommandInteraction):
    pass

  @projects.sub_command(name="add", description=Strings.common_add_project_brief)
  async def add_project(self, inter: disnake.CommandInteraction):
    await inter.response.send_modal(modal=disnake.ui.Modal(title="Add project", custom_id="add_project_modal",
                                                           components=
                                                           [
                                                             disnake.ui.TextInput(label="Name", custom_id="name", max_length=128, min_length=1),
                                                             disnake.ui.TextInput(label="Description", custom_id="description", max_length=4000, min_length=1)
                                                           ]))

  @staticmethod
  async def projects_list_autocomplete(_, search_string: str):
    projects = projects_repo.get_all()
    project_names = [project.name for project in projects]
    if search_string is None or search_string == "":
      return project_names
    return [project_name for project_name in project_names if search_string in project_name]

  @projects.sub_command(name="remove", description=Strings.common_remove_project_brief)
  async def remove_project(self, inter: disnake.CommandInteraction, project_name: str=commands.Param(autocomplete=projects_list_autocomplete, description="Name of project to delete")):
    if projects_repo.remove_project(project_name):
      await general_util.generate_success_message(inter, Strings.populate_string("common_remove_project_removed", name=project_name))
    else:
      await general_util.generate_error_message(inter, Strings.populate_string("common_remove_project_failed", name=project_name))

  @projects.sub_command(name="get", description=Strings.common_project_get_brief)
  async def project_get(self, inter: disnake.CommandInteraction, project_name: str=commands.Param(autocomplete=projects_list_autocomplete, description="Name of project to show")):
    project = projects_repo.get_by_name(project_name)
    if project is None:
      return await general_util.generate_error_message(inter, Strings.populate_string("common_project_get_not_found", name=project_name))

    embed = disnake.Embed(title=project.name, description=project.description, color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, inter.author)

    await inter.send(embed=embed)

  @commands.Cog.listener()
  async def on_modal_submit(self, inter: disnake.ModalInteraction):
    if inter.custom_id == "add_project_modal":
      project = projects_repo.add_project(project_name=inter.text_values["name"], project_description=inter.text_values["description"])
      if project is None:
        await general_util.generate_error_message(inter, Strings.populate_string("common_add_project_failed", name=inter.text_values["name"]))
      else:
        await general_util.generate_success_message(inter, Strings.populate_string("common_add_project_added", name=inter.text_values["name"]))

def setup(bot):
  bot.add_cog(Common(bot))
