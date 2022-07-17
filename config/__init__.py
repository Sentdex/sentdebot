from . import config_loader
from . import cooldowns

config = config_loader.Config.from_toml("config/config.toml", "config/config.template.toml")
