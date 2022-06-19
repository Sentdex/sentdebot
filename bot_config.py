import os
from typing import NamedTuple
from json import loads, dumps
from bot_definitions import Channel, Role, ChatBot, channels, roles, chatbots


class BotConfig(NamedTuple):
    path: str
    token: str
    prefix: str

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
        print(json_dict)
        # convert to namedtuple
        json_dict['channels'] = [Channel(**c) for c in json_dict['channels']]
        json_dict['roles'] = [Role(**r) for r in json_dict['roles']]
        json_dict['chatbots'] = [ChatBot(**b) for b in json_dict['chatbots']]
        return cls(**json_dict)


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
                    os.remove(os.path.join(save_path, 'config.json'))
                else:
                    return

        os.makedirs(save_path, exist_ok=True)
        with open(os.path.join(save_path, 'config.json'), 'w') as f:
            f.write(cls(
                path=save_path,
                token=input('Enter your bot token: ') if token is None else token,
                prefix='sentdebot.',
                intents=32767,
                resample_interval='60min',
                days_to_keep=21,
                top_user_count=10,
                channels=channels,
                roles=roles,
                chatbots=chatbots,
            ).to_json())

def get_config(save_path):
    if not os.path.exists(save_path):
        BotConfig.setup_config(save_path)
    with open(os.path.join(save_path, 'config.json'), 'r') as f:
        return BotConfig.from_json(f.read())

if __name__ == '__main__':
    BotConfig.setup_config('sentdebot')
    print('Config setup complete.')
