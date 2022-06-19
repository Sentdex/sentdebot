"""Core bot definition stuff, such as channels, roles and commands.
Intended purpose to use dependency injection to expand and test the bot.
"""

from bot_definitions.definitions import Command, Role, Channel, Channel_Type, ChatBot
from bot_definitions.roles import roles
from bot_definitions.channels import channels
from bot_definitions.bots import chatbots
from bot_definitions.commands import available_commands, register_as_command

__all__ = [
    'Command',
    'Role',
    'Channel',
    'Channel_Type',
    'ChatBot',
    'available_commands',
    'register_as_command',
    'roles',
    'channels',
    'chatbots'
]

