# Parsing and storing of config

import os
import toml

class Config:
  @classmethod
  def parse(cls, obj):
    if isinstance(obj, list):
      return [cls.parse(v) for v in obj]
    elif isinstance(obj, dict):
      result = cls()
      for k,v in obj.items():
        setattr(result, k, cls.parse(v))
      return result
    else:
      return obj

  @classmethod
  def from_toml(cls, *paths, **kwargs):
    existing_paths = [*filter(os.path.exists, paths)]
    if len(existing_paths) == 0:
      raise ValueError(f'none of {paths} were found')
    return cls.parse(toml.load(existing_paths[0], **kwargs))
