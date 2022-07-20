# Parsing and storing of config

import os
import toml

class Config:
  def to_dict(self):
    def convert(value):
      if isinstance(value, Config):
        return value.to_dict()
      elif isinstance(value, list):
        return [convert(item) for item in value]
      else:
        return value

    return { attr: convert(getattr(self, attr)) for attr in self.__exportable__   }

  def __repr__(self):
    return f'{type(self).__name__}.parse({self.to_dict()!r})'

  def write(self, path):
    with open(path, "w", encoding="utf-8") as fd:
      toml.dump(self.to_dict(), fd)

  @classmethod
  def parse(cls, obj):
    if isinstance(obj, list):
      return [cls.parse(v) for v in obj]
    elif isinstance(obj, dict):
      result = cls()
      result.__exportable__ = []
      for k, v in obj.items():
        result.__exportable__.append(k)
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
