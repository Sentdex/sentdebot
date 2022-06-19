import os
from typing import NamedTuple
from json import loads, dumps
from bot_definitions import Channel, Role, ChatBot, channels, roles, chatbots


class BotConfig(NamedTuple):
    path: str
    token: str
    prefix: str

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
        return cls(**loads(json_str))

    @classmethod
    def setup_config(cls, save_path):
        if os.path.exists(save_path):
            if os.path.exists(os.path.join(save_path, 'config.json')):
                if input('Overwrite existing config? [y/n] ') == 'y':
                    os.remove(os.path.join(save_path, 'config.json'))
                else:
                    return

        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, 'config.json'), 'w') as f:
            f.write(cls(
                path=save_path,
                token=input('Enter your bot token: '),
                prefix='sentdebot.',
                resample_interval='60min',
                days_to_keep=21,
                top_user_count=10,
                channels=channels,
                roles=roles,
                chatbots=chatbots,
            ).to_json())


if __name__ == '__main__':
    BotConfig.setup_config('sentdebot')