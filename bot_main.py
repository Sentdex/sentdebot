import os

import nextcord
from nextcord.ext import commands

from bot_config_protocols import ReadOnlyConfig

default_bot_config = {

    "nextcord_client_id": "",
    "nextcord_client_secret": "",
    "nextcord_redirect_uri": "",

    "bot_token": "",  # bot token from oauth.com/developers/applications/
    "bot_name": "",  # bot name
    "bot_prefix": "",  # bot prefix
    "bot_prefix_allow_trim_white_space": False,  # allow bot prefix to be trimmed of whitespace after prefix
    "bot_prefix_case_insensitive": True,  # bot prefix is case-insensitive

    "bot_presence_comment": "",  # bot presence is enabled

    "default_channel_layout": {  # default channel layout
        "general": [  # Category -> [Channel, ...]
            ("chat", "text"),  # Channel -> (Name, Type)
            ("off_topic", "text"),
            ("announcements", "text"),
            ("bot_commands", "text"),
            ("voice_chat", "voice")
        ]
    },

    "default_roles": {  # default roles
        "admin": "admin",
        "moderator": "moderator",
        "bot_admin": "bot",
        "bot_moderator": "bot"
    },

    "cog_folder": "cogs",
    "secret_key": "",

    "guild_id": 0
}


class Bot(commands.Bot):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return getattr(cls, 'instance')

    def __init__(self, config=ReadOnlyConfig("config", default_bot_config)):
        super().__init__(command_prefix=config.get('bot_prefix'), intents=nextcord.Intents.all())
        self.config = config
        self.cog_file_update_times = {}

    def cog_loader(self):
        try:
            if not os.path.exists('core_cogs'):
                os.makedirs('core_cogs')
            for file in os.listdir('core_cogs'):
                if file.startswith('cog_'):
                    if file.endswith('.py'):
                        self.load_extension(f'core_cogs.{file[:-3]}')
                    elif os.path.isdir(os.path.join('core_cogs', file)):
                        for init_file in os.listdir(os.path.join('core_cogs', file)):
                            if init_file.startswith('__init__'):
                                self.load_extension(f'core_cogs.{file}.{init_file[:-3]}')
        except Exception as e:
            print(f'Error loading cogs: {e}')
            quit()
        if not os.path.exists('cogs'):
            os.makedirs('cogs')
        for file in os.listdir('cogs'):
            if file.startswith('cog_'):
                try:
                    if os.path.isdir(os.path.join('cogs', file)):
                        for init_file in os.listdir(os.path.join('cogs', file)):
                            if init_file.startswith('__init__'):
                                self.load_extension(f'cogs.{file}.{init_file[:-3]}')
                                self.cog_file_update_times[file] = os.path.getmtime(f'cogs/{file}/{init_file}')
                    elif file.endswith('.py'):
                        self.load_extension(f'cogs.{file[:-3]}')
                        self.cog_file_update_times[file[:-3]] = os.path.getmtime(f'cogs/{file}')
                except Exception as e:
                    print(f'Error loading cog: {e}')
                    continue

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def run(self):
        self.cog_loader()
        super().run(self.config.get('bot_token'))

    def logout(self):
        self.loop.stop()
        self.close()


if __name__ == '__main__':
    bot = Bot()
    bot.run()
