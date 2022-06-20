import os
from functools import cache
from typing import NamedTuple
from json import loads, dumps
from bot_definitions import Channel, Role, ChatBot, channels, roles, chatbots


class BotConfig(NamedTuple):
    path: str
    token: str
    prefix: str
    guild_id: int

    intents: int

    resample_interval: str

    days_to_keep: int
    top_user_count: int

    channels: list[Channel]
    roles: list[Role]
    chatbots: list[ChatBot]


    def to_json(self):
        return dumps(self._asdict(), indent=4)

    @classmethod
    def from_json(cls, json_str):
        json_dict = loads(json_str)
        # convert  channels, roles, chatbots to their namedtuples
        for key, entry_type in [('channels', Channel), ('roles', Role), ('chatbots', ChatBot)]:
            json_dict[key] = [entry_type._make(entry) for entry in json_dict[key]]
            print(json_dict[key])
        return cls(**json_dict)

    def as_dict(self):
        return self._asdict()


    @classmethod
    def setup_config(cls, save_path):
        token = None
        if os.path.exists(save_path):
            if os.path.exists(os.path.join(save_path, 'config.json')):
                if input('Overwrite existing config? [y/n] ') == 'y':
                    if input('do you wish to save your token? [y/n] ') == 'y':
                        # get the token
                        with open(os.path.join(save_path, 'config.json'), 'r') as f:
                            json_dict = loads(f.read())
                            token = json_dict['token']
                else:
                    return

        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, 'config.json'), 'w') as f:
            f.write(cls(
                path=save_path,
                token=input('Enter your bot token: ') if token is None else token,
                prefix='sentdebot.',
                guild_id=405403391410438165,
                intents=32767,
                resample_interval='60min',
                days_to_keep=21,
                top_user_count=10,
                channels=channels,
                roles=roles,
                chatbots=chatbots,
            ).to_json())

    @classmethod
    @cache
    def get_config(cls, save_path):
        if not os.path.exists(save_path):
            cls.setup_config(save_path)
        with open(os.path.join(save_path, 'config.json'), 'r') as f:
            return cls.from_json(f.read())


__all__ = ['BotConfig']

if __name__ == '__main__':
    BotConfig.setup_config('sentdebot')
    print('Config setup complete.')
