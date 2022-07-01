# a oauth.py commands bot
import logging
import os

import nextcord
from nextcord.ext import commands

from bot_config_manager import ReadOnlyConfig, Config


class Bot:
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        return getattr(cls, 'instance')

    def __init__(self, config):
        self.config = config

        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}.{self.config.get('bot_name')}")
        if self.config.get('save_logs'):
            if not os.path.exists('logs'):
                os.makedirs('logs')
            path = os.path.join(self.config.get('logs_folder'), f'{self.config.get("bot_name")}.log')
            file_handler = logging.FileHandler(path)
            file_handler.setLevel(self.config.get('log_level'))
            file_handler.setFormatter(logging.Formatter(self.config.get('log_format')))
            self.logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(self.config.get('log_level'))
        console_handler.setFormatter(logging.Formatter(self.config.get('log_format')))
        self.logger.addHandler(console_handler)
        self.logger.setLevel(self.config.get('log_level'))
        self.client = commands.Bot(command_prefix=self.config.get('bot_prefix'), intents=nextcord.Intents.all())
        self.client.remove_command('help')

    def cog_loader(self):
        try:
            if not os.path.exists('core_cogs'):
                os.makedirs('core_cogs')
            for file in os.listdir('./core_cogs'):
                if file.startswith('cog_') and file.endswith('.py'):
                    self.client.load_extension(f'core_cogs.{file[:-3]}')
        except Exception as e:
            # self.logger.error(f"Failed to load core cogs: {e}")
            raise e
        if not os.path.exists('cogs'):
            os.makedirs('cogs')
        for file in os.listdir('./cogs'):
            if file.startswith('cog_') and file.endswith('.py'):
                try:
                    self.client.load_extension(f'cogs.{file[:-3]}')
                except Exception as e:
                    # self.logger.error(f"Failed to load cogs: {e}")
                    raise e

    def __enter__(self):
        self.run()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def run(self):
        self.cog_loader()
        self.client.run(self.config.get('bot_token'))

    def close(self):
        self.client.close()


if __name__ == '__main__':
    config = ReadOnlyConfig()
    bot = Bot(config)
    bot.run()