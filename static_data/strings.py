# Storage for all static strings

from config import config


class callable_string(str):
  __call__ = str.format

class formattable(type):
  def __init__(cls, clsname, superclasses, attributedict):
    cls.clsname = clsname

  def __getattribute__(cls, key):
    try:
      return callable_string(object.__getattribute__(cls, key))
    except AttributeError:
      raise AttributeError(f'{cls.clsname} class has no attribute {key}')


class Strings(metaclass=formattable):
  # System
  system_load_brief = "Load unloaded extension"
  system_load_help = "Instead of extension name can be used \"all\" to load all extensions at once"
  system_unable_to_load_cog = "Unable to load {cog} extension\n`{e}`"
  system_cog_loaded = "Extension {extension} loaded"

  system_unload_brief = "Unload loaded extension"
  system_unload_help = "Instead of extension name can be used \"all\" to unload all extensions at once"
  system_unload_protected_cog = "Unable to unload {extension} extension - protected"
  system_unable_to_unload_cog = "Unable to unload {cog} extension\n`{e}`"
  system_cog_unloaded = "Extension {extension} unloaded"

  system_reload_brief = "Reload loaded extension"
  system_reload_help = "Instead of extension name can be used \"all\" to reload all extensions at once"
  system_unable_to_reload_cog = "Unable to reload {cog} extension\n`{e}`"
  system_cog_reloaded = "Extension {extension} reloaded"

  system_cogs_brief = "Show all extensions and their states"

  system_logout_brief = "Turn off bot"

  # Help
  help_brief = "Show all commands and help for them"
  help_help = "Also you can specify module to show help only for specific module"

  # Errors
  error_unknown_command = f'Unknown command - use {config.command_prefixes[0]}help for all commands'
  error_command_on_cooldown = 'This command is on cooldown. Please wait {remaining}s'
  error_missing_permission = 'You do not have the permissions to use this command.'
  error_missing_role = 'You do not have {role} role to use this command'
  error_missing_argument = 'Missing {argument} argument of command\n{signature}'
  error_bad_argument = f'Some arguments of command missing or wrong, use {config.command_prefixes[0]}help to get more info'
  error_max_concurrency_reached = "Bot is busy, try it later"
  error_no_private_message = "This command can't be used in private channel"
  error_interaction_timeout = "Interaction took more than 3 seconds to be responded to. Try again later."

  # Common
  common_ping_brief = "Ping the bot and get bot and api latency"

  common_member_count_brief = "Show number of members on server"

  common_search_brief = "Search on Sentdex webpage"
  common_search_nothing_found = "Nothing found for search term `{term}`"

  # Projects
  projects_project_get_brief = "Get project by name"
  projects_project_get_not_found = "Project `{name}` is not in database"

  projects_add_project_brief = "Add project to database of projects"
  projects_add_project_added = "Project `{name}` added to database of projects"
  projects_add_project_failed = "Project `{name}` already exists in database"

  projects_remove_project_brief = "Remove project from database of projects"
  projects_remove_project_removed = "Project `{name}` removed from database of projects"
  projects_remove_project_failed = "Project `{name}` not found for removal"

  # Stats
  stats_user_activity_brief = "Show recent user activity in channels"

  stats_community_report_brief = "Show recent numbers of users on server"

  stats_main_guild_not_set = "Main guild is not loaded"

  # Help Threader
  help_threader_announcement = "```Help channel now using threads for solving problems so use them and post new message outside of this thread only if thread gets locked (after 3 days) or with different problem. Thank you```"

  help_threader_request_create_brief = "Create new help request"
  help_threader_request_create_failed = "Creation of help request failed, try it later"
  help_threader_request_create_passed = "Your request was created, you were added to that thread and here is your [LINK]({link})"

  help_threader_list_requests_brief = "List all opened help requests"
  help_threader_list_requests_no_help_required = "*There are no threads that need help*"

  help_threader_request_solved_brief = "Mark current help request as solved"
  help_threader_request_solved_not_found = "Invalid place for this command\nThis command should be called in your own opened help request thread to mark it as solved"
  help_threader_request_solved_not_owner = "You are not owner of this help request\nThis command should be called in your own opened help request thread to mark it as solved"
  help_threader_request_solved_closed = "Help request marked as solved"

  help_threader_help_channel_not_found = "Help channel not found"

  # Code Execute
  code_execute_run_brief = "Evaluate code"
  code_execute_run_help = "Code to execute should always be in markdown with specified language\nCode block can be as a part of command (under the command) or the command can be called in reply message to that codeblock"
  code_execute_run_cant_find_reference_channel = "Can't find reference channel of reply"
  code_execute_run_cant_find_reference_message = "Can't find reference message of reply"
  code_execute_run_cant_find_code_block = "Can't find codeblock in message"
  code_execute_run_cant_find_language_in_code_block = "Can't find language in codeblock"
  code_execute_run_failed_to_get_api_response = "Failed to get response from API"
