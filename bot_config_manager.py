# utils to save and load configs, if folder configs doesn't exist, create it
import os
from json import loads, dumps
from types import MappingProxyType

from typing import Protocol, Any

# ALL ENTRIES IN CLASS READ_ONLY
default_config = {

    "discord_client_id": "",
    "discord_client_secret": "",
    "discord_redirect_uri": "",

    "bot_token": "",  # bot token from oauth.com/developers/applications/
    "bot_name": "",  # bot name

    "bot_prefix": "",  # bot prefix
    "bot_prefix_allow_trim_white_space": False,  # allow bot prefix to be trimmed of whitespace after prefix
    "bot_prefix_case_insensitive": True,  # bot prefix is case-insensitive

    "bot_presence_comment": "",  # bot presence is enabled

    "guild_id": "",  # guild id

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
    "enabled_cogs": [],

    "save_metrics": False,
    "save_interval": 60,
    "metrics_folder": "metrics",
    "metrics_keep_history_length_days": 21,

    "save_logs": False,
    "logs_folder": "logs",
    "log_level": "INFO",
    "log_dateformat": "%Y-%m-%d %H:%M:%S",
    "log_format": "%(asctime)s,%(levelname)s,%(message)s",
    "log_max_size": 1000000,

    "management_panel": False,
    "management_panel_host": "localhost",
    "management_panel_port": 5000,
    "management_panel_session": os.urandom(24).hex(),

    "database_path": "",

}


class Config(Protocol):
    def get(self, key) -> Any:
        ...


class ReadOnlyConfig:

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return getattr(cls, 'instance')

    def __init__(self, config_mapping=None):
        config = config_mapping or default_config
        try:
            if not os.path.exists('configs'):
                os.makedirs('configs')
            if not os.path.exists('configs/config.json'):
                with open('configs/config.json', 'w') as config_file:
                    config_file.write(dumps(config, indent=4))
                    print('Please fill in the config.json file')
                    quit()
            with open('configs/config.json', 'r') as config_file:
                json_in = loads(config_file.read())
                for key in json_in:
                    if key not in config:
                        print(f'{key} is not a valid key')
                    else:
                        config[key] = json_in[key]
            # if token is not set, quit
            if not config['bot_token']:
                raise Exception('bot_token is not set')
            # if save_metrics is set to true, create metrics folder
            if config['save_metrics']:
                if not os.path.exists('metrics'):
                    os.makedirs('metrics')
            # if save_logs is set to true, create logs folder
            if config['save_logs']:
                if not os.path.exists('logs'):
                    os.makedirs('logs')
        except Exception as e:
            print(f'Error loading config: {e}')
            quit()
        finally:
            with open('configs/config.json', 'w') as config_file:
                config_file.write(dumps(config, indent=4))
            self.config = MappingProxyType(config)

    def get(self, key) -> Any:
        return self.config[key]
