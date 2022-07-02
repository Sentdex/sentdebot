# utils to save and load configs, if folder configs doesn't exist, create it
import os
from json import loads, dumps
from types import MappingProxyType

from typing import Protocol, Any


# ALL ENTRIES IN CLASS READ_ONLY

class Config(Protocol):
    def get(self, key) -> Any:
        ...

    def __getitem__(self, key) -> Any:
        ...


class ReadOnlyConfig:
    """Creates a restricted read only dictionary mapping"""
    def __init__(self, filename, config_mapping):
        self.filename = filename
        config = config_mapping
        try:
            if not os.path.exists('configs'):
                os.makedirs('configs')
            if not os.path.exists(f'configs/{filename}.json'):
                with open(f'configs/{filename}.json', 'w') as config_file:
                    config_file.write(dumps(config, indent=4))
                    print('Please fill in the config.json file')
                    quit()
            with open(f'configs/{filename}.json', 'r') as config_file:
                json_in = loads(config_file.read())
                for key in json_in:
                    if key not in config:
                        print(f'{key} is not a valid key')
                    else:
                        config[key] = json_in[key]
        except Exception as e:
            print(f'Error loading config: {e}')
            quit()
        finally:
            with open(f'configs/{filename}.json', 'w') as config_file:
                config_file.write(dumps(config, indent=4))
            self.config = MappingProxyType(config)

    def get(self, key) -> Any:
        return self.config[key]

    def __getitem__(self, key) -> Any:
        return self.config[key]


class BoundConfig:
    # similar to read only config, except mutable and writes config changes directly to file, ugly, risy you probably shouldn't use this outside of testing purposes

    def __init__(self, filename, config_mapping):
        self.filename = filename
        config = config_mapping
        try:
            if not os.path.exists('configs'):
                os.makedirs('configs')
            if not os.path.exists(f'configs/{filename}.json'):
                with open(f'configs/{filename}.json', 'w') as config_file:
                    config_file.write(dumps(config, indent=4))
                    print('Please fill in the config.json file')
                    quit()
            with open(f'configs/{filename}.json', 'r') as config_file:
                json_in = loads(config_file.read())
                for key in json_in:
                    if key not in config:
                        print(f'{key} is not a valid key')
                    else:
                        config[key] = json_in[key]
        except Exception as e:
            print(f'Error loading config: {e}')
            quit()
        finally:
            with open(f'configs/{filename}.json', 'w') as config_file:
                config_file.write(dumps(config, indent=4))
            self.config = config

    def get(self, key) -> Any:
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value
        with open(f'configs/{self.filename}.json', 'w') as config_file:
            config_file.write(dumps(self.config, indent=4))

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value
        with open(f'configs/{self.filename}.json', 'w') as config_file:
            config_file.write(dumps(self.config, indent=4))

    # print copy pasteable dict representation of config
    def __str__(self):
        return dumps(self.config, indent=4)
