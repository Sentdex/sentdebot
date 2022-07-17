# Parsing and storing of config

import os
import toml


class Config:
  @classmethod
  def parse(cls, dct):
    result = cls()
    for k,v in dct.items():
      if isinstance(v, dict):
        v = cls.parse(v)
      setattr(result, k, v)
    return result

  @classmethod
  def from_toml(cls, *paths, **kwargs):
    existing_paths = [*filter(os.path.exists, paths)]
    if len(existing_paths) == 0:
      raise ValueError(f'none of {paths} were found')
    return cls.parse(toml.load(existing_paths[0], **kwargs))
