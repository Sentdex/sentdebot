from typing import NamedTuple
from json import loads, dumps
from bot_definitions import Channel, Role, ChatBot


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
        return dumps(self._asdict())

    @classmethod
    def from_json(cls, json_str):
        return cls(**loads(json_str))

    @classmethod
    def default_json(cls, save_path):
        string = cls(
            path='',
            token='',
            prefix='!',
            resample_interval='1h',
            days_to_keep=0,
            top_user_count=0,
            channels=[],
            roles=[],
            chatbots=[],
        ).to_json()
        with open(save_path, 'w') as f:
            f.write(string)

