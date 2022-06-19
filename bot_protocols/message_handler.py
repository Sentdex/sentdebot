# import Protocols
from typing import Protocol


class MessageHandler(Protocol):
    def handle_message(self, message):
        pass


class CommandHandler(Protocol):
    def handle_command(self, command):
        pass
