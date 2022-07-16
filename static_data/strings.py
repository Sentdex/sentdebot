# Storage for all static strings

from config import config

class Strings:
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

  # Common
  common_member_count_brief = "Show number of members on server"

  common_search_brief = "Search on Sentdex webpage"
  common_search_nothing_found = "Nothing found for search term `{term}`"

  common_project_get_brief = "Get project by name"
  common_project_get_not_found = "Project `{name}` is not in database"

  common_add_project_brief = "Add project to database of projects"
  common_add_project_added = "Project `{name}` added to database of projects"
  common_add_project_failed = "Project `{name}` already exists in database"

  common_remove_project_brief = "Remove project from database of projects"
  common_remove_project_removed = "Project `{name}` removed from database of projects"
  common_remove_project_failed = "Project `{name}` not found for removal"

  # Stats
  stats_user_activity_brief = "Show recent user activity in channels"

  stats_community_report_brief = "Show recent numbers of users on server"

  stats_main_guild_not_set = "Main guild is not loaded"

  # Help Threader
  help_threader_announcement = "```Help channel now using threads for solving problems so use them and post new message outside of this thread only if thread gets locked (after 3 days) or with different problem. Thank you```"

  help_threader_list_requests_brief = "List all opened help requests"
  help_threader_list_requests_no_help_required = "*There are no threads that need help*"

  help_threader_request_solved_brief = "Mark current help request as solved"
  help_threader_request_solved_not_found = "Invalid place for this command\nThis command should be called in your own opened help request thread to mark it as solved"
  help_threader_request_solved_not_owner = "You are not owner of this help request\nThis command should be called in your own opened help request thread to mark it as solved"
  help_threader_request_solved_closed = "Help request marked as solved"

  @staticmethod
  def populate_string(message_name, *args, **kwargs):
    try:
      template = getattr(Strings, message_name)
      return template.format(*args, **kwargs)
    except AttributeError:
      raise ValueError(f"Invalid template {message_name}")