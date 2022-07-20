# Storage for all static strings

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
  system_unable_to_load_cog = "Unable to load {cog} extension\n`{e}`"
  system_cog_loaded = "Extension {extension} loaded"

  system_unload_brief = "Unload loaded extension"
  system_unload_protected_cog = "Unable to unload {extension} extension - protected"
  system_unable_to_unload_cog = "Unable to unload {cog} extension\n`{e}`"
  system_cog_unloaded = "Extension {extension} unloaded"

  system_reload_brief = "Reload loaded extension"
  system_unable_to_reload_cog = "Unable to reload {cog} extension\n`{e}`"
  system_cog_reloaded = "Extension {extension} reloaded"

  system_cogs_brief = "Show all extensions and their states"

  system_logout_brief = "Turn off bot"

  system_pull_brief = "Pull latest code from github"

  # Help
  help_description = "Show all message commands and help for them"

  help_dummy_help_brief = "Show description default functions of bot"
  help_dummy_help_text = "Hello there\nThis is not real help as you can see\nThis is dummy placeholder to tell you how this bot works\nIf you want to see all message commands then use slash commands for thar '/help' and there are more slash commands that you can see after typing '/' to chat\nHave a nice day"

  help_commands_list_description = "Show list of all available message commands"

  # Errors
  error_unknown_command = f'Unknown command - use /help for all commands'
  error_command_on_cooldown = 'This command is on cooldown. Please wait {remaining}s'
  error_missing_permission = 'You do not have the permissions to use this command.'
  error_missing_role = 'You do not have {role} role to use this command'
  error_missing_argument = 'Missing {argument} argument of command\n{signature}'
  error_bad_argument = f'Some arguments of command missing or wrong, use /help to get more info'
  error_max_concurrency_reached = "Bot is busy, try it later"
  error_no_private_message = "This command can't be used in private channel"
  error_interaction_timeout = "Interaction took more than 3 seconds to be responded to. Try again later."
  error_forbiden = "Bot can't do this action"

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

  # Voice channel notifier
  voice_channel_notifier_single_user = "{nick} started something big in {channel}"
  voice_channel_notifier_multiple_users = "{nicks} started something big in {channel}"

  voice_channel_notifier_subscribe_brief = "Subscribe to receive voice chat notifications"
  voice_channel_notifier_subscribe_invalid_channel = "Channel {channel} is not available for subscription"
  voice_channel_notifier_subscribe_role_not_found = "Role for channel {channel} not found"
  voice_channel_notifier_subscribe_add_role_failed = "Subscription failed"
  voice_channel_notifier_subscribe_add_role_success = "Subscribed to {channel}"

  voice_channel_notifier_unsubscribe_brief = "Unsubscribe from receiving voice chat notifications"
  voice_channel_notifier_unsubscribe_invalid_channel = "Channel {channel} is not available for unsubscription"
  voice_channel_notifier_unsubscribe_role_not_found = "Role for channel {channel} not found"
  voice_channel_notifier_unsubscribe_remove_role_failed = "Unsubscription failed"
  voice_channel_notifier_unsubscribe_remove_role_success = "Unsubscribed from {channel}"
