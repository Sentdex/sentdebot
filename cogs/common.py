import math

import disnake
from disnake.ext import commands
from requests_html import HTMLSession

from config import cooldowns
from static_data.strings import Strings
from features.base_cog import Base_Cog
from util import general_util
from database import projects_repo
from features.paginator import PaginatorSession

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

  @commands.group(pass_context=True, brief=Strings.common_projects_brief)
  async def projects(self, ctx: commands.Context):
    if ctx.invoked_subcommand is None:
      all_projects = projects_repo.get_all()

      number_of_projects = len(all_projects)
      number_of_batches = math.ceil(number_of_projects / 5)
      batches = [all_projects[i * 5: i * 5 + 5] for i in range(number_of_batches)]

      pages = []
      for batch in batches:
        embed = disnake.Embed(title="List of projects", color=disnake.Color.dark_blue())
        general_util.add_author_footer(embed, ctx.author)

        for project in batch:
          embed.add_field(name=project.name, value=project.description, inline=False)
        pages.append(embed)

      if not pages:
        await general_util.generate_error_message(ctx, Strings.common_projects_empty)
      else:
        await PaginatorSession(self.bot, ctx, timeout=120, pages=pages).run()

  @projects.command(name="get", brief=Strings.common_project_get_brief)
  async def get_project(self, ctx: commands.Context, project_name: str):
    await general_util.delete_message(self.bot, ctx)

    project = projects_repo.get_by_name(project_name)
    if project is None:
      return await general_util.generate_error_message(ctx, Strings.populate_string("common_project_get_not_found", name=project_name))

    embed = disnake.Embed(title=project.name, description=project.description, color=disnake.Color.dark_blue())
    general_util.add_author_footer(embed, ctx.author)

    await ctx.send(embed=embed)

  @projects.command(name="add", brief=Strings.common_add_project_brief, help=Strings.common_add_project_help)
  @commands.check(general_util.is_mod)
  async def add_project(self, ctx: commands.Context, project_name: str, *, project_description: str):
    await general_util.delete_message(self.bot, ctx)

    project = projects_repo.add_project(project_name, project_description)
    if project is None:
      await general_util.generate_error_message(ctx, Strings.populate_string("common_add_project_failed", name=project_name))
    else:
      await general_util.generate_success_message(ctx, Strings.populate_string("common_add_project_added", name=project_name))

  @projects.command(name="remove", brief=Strings.common_remove_project_brief, help=Strings.common_remove_project_help)
  @commands.check(general_util.is_mod)
  async def remove_project(self, ctx: commands.Context, project_name: str):
    await general_util.delete_message(self.bot, ctx)

    if projects_repo.remove_project(project_name):
      await general_util.generate_success_message(ctx, Strings.populate_string("common_remove_project_removed", name=project_name))
    else:
      await general_util.generate_error_message(ctx, Strings.populate_string("common_remove_project_failed", name=project_name))


def setup(bot):
  bot.add_cog(Common(bot))
