import toml
from typing import List
import os

def get_attr(toml_config: dict, section: str, attr_key: str):
  val = toml_config[section][attr_key]
  if val == "<env>":
    val = os.getenv(f"{section}_{attr_key}")
  return val

def get_config() -> dict:
  try:
    return dict(toml.load("config/config.toml", _dict=dict))
  except:
    return dict(toml.load("config/config.template.toml", _dict=dict))

class Config:
  raw_config = get_config()

  key: str = get_attr(raw_config, "base", "discord_api_key")
  status_message: str = get_attr(raw_config, "base", "status_message")
  command_prefixes: List[str] = get_attr(raw_config, "base", "command_prefixes")
  log_to_file: bool = get_attr(raw_config, "base", "log_to_file")
  log_channel_id: int = get_attr(raw_config, "base", "log_channel_id")
  error_duration: int = get_attr(raw_config, "base", "error_duration")
  success_duration: int = get_attr(raw_config, "base", "success_duration")

  admin_role_id: int = get_attr(raw_config, "ids", "admin_role_id")
  mod_role_id: int = get_attr(raw_config, "ids", "mod_role_id")

  protected_cogs: List[str] = get_attr(raw_config, "cogs", "protected_cogs")