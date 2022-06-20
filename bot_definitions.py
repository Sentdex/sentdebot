from typing import NamedTuple, Literal, Callable

########################################################################################################################

ChannelType = Literal['text', 'voice']
ChannelTag = Literal['community', 'general', 'help', 'image']


class Channel(NamedTuple):
    name: str
    id: int
    channel_type: ChannelType
    tags: tuple[ChannelTag, ...]

    # defaults
    count_top_users: bool = False


RoleType = Literal['admin', 'mod', 'vanity']

Role = NamedTuple(
    'Role', [
        ('name', str),
        ('id', int),
        ('role_type', RoleType),
    ]
)

ChatBot = NamedTuple(
    'ChatBot', [
        ('name', str),
        ('id', int)
    ]
)
########################################################################################################################

roles = [
    Role('Admin', 405506750654054401, 'admin'),
    Role('Mod', 405520180974714891, 'mod'),

    Role('baby python', 479433667576332289, 'vanity'),
    Role('import this', 501115079572324352, 'vanity'),
    Role('guido', 501114928854204431, 'vanity'),
    Role('whitespace', 501114732057460748, 'vanity'),
    Role('holy grail', 501115820273958912, 'vanity'),
    Role('monty', 479433667576332289, 'vanity'),
    Role('py3ftw', 501115401577431050, 'vanity'),
]
########################################################################################################################

channels = [
    Channel('__init__', 476473718479257620, 'text', ('community',)),

    Channel('__main__', 408713676095488000, 'text', ('general', 'community'), True),
    Channel('show_and_tell', 767379896040161290, 'text', ('general', 'community')),

    Channel('help', 412620789133606914, 'text', ('help', 'community'), True),
    Channel('help_0', 412620789133606914, 'text', ('help', 'community')),
    Channel('help_1', 507281643606638622, 'text', ('help', 'community')),
    Channel('help_2', 682674227664388146, 'text', ('help', 'community')),
    Channel('help_3', 843130901998469177, 'text', ('help', 'community')),

    Channel('dogs', 671016601440747520, 'text', ('general', 'community')),

    Channel('voice-channel-text', 484406428233367562, 'voice', ('general', 'community')),

]
########################################################################################################################

chatbots = [
    ChatBot('Charles', 405511726050574336),
    ChatBot('Irene', 428904098985803776),
    ChatBot('Charlene', 414630095911780353),
]


########################################################################################################################

def get_all_channels_by_tag(tag: Literal) -> list:
    return [channel for channel in channels if tag in channel.tags]


def get_all_channels_by_type(channel_type: str) -> list:
    return [channel for channel in channels if channel.channel_type == channel_type]


def get_all_roles_by_type(role_type: str) -> list:
    return [role for role in roles if role.role_type == role_type]


__all__ = [  # to not pollute imports
    'Role',
    'Channel',
    'ChatBot',
    'roles',
    'channels',
    'chatbots',
    'get_all_channels_by_tag',
    'get_all_channels_by_type',
    'get_all_roles_by_type',
]
