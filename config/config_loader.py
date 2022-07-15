# Parsing and storing of config

import toml
from typing import List
import os

def get_attr(toml_config: dict, section: str, attr_key: str):
  val = toml_config[section][attr_key]
  if val == "<env>":
    val = os.getenv(f"{section}_{attr_key}")
  return val

def get_config() -> dict:
  # Get config
  # If config is not present try to load template of config
  try:
    return dict(toml.load("config/config.toml", _dict=dict))
  except:
    return dict(toml.load("config/config.template.toml", _dict=dict))

class Config:
  raw_config = get_config()

  main_guild_id = get_attr(raw_config, "base", "main_guild_id")
  key: str = get_attr(raw_config, "base", "discord_api_key")
  status_message: str = get_attr(raw_config, "base", "status_message")
  command_prefixes: List[str] = get_attr(raw_config, "base", "command_prefixes")
  log_to_file: bool = get_attr(raw_config, "base", "log_to_file")
  log_channel_id: int = get_attr(raw_config, "base", "log_channel_id")
  error_duration: int = get_attr(raw_config, "base", "error_duration")
  success_duration: int = get_attr(raw_config, "base", "success_duration")
  database_connect_string: str = get_attr(raw_config, "base", "database_connect_string")

  admin_role_ids: List[int] = get_attr(raw_config, "ids", "admin_role_ids")
  mod_role_ids: List[int] = get_attr(raw_config, "ids", "mod_role_ids")

  protected_cogs: List[str] = get_attr(raw_config, "cogs", "protected_cogs")
  defaul_loaded_cogs: List[str] = get_attr(raw_config, "cogs", "defaul_loaded_cogs")

  role_giver_role_ids: List[int] = get_attr(raw_config, "random_role_giver", "role_ids")
  role_giver_give_chance: float = get_attr(raw_config, "random_role_giver", "chance")