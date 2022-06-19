from typing import NamedTuple, Literal, Callable

# module to define definitions for other modules Only
Channel_Type = Literal['text', 'voice']
Role_Type = Literal['admin', 'mod', 'vanity']


class Channel(NamedTuple):
    name: str
    id: int
    channel_type: Channel_Type
    tags: tuple[Literal['community', 'general', 'help', 'image'], ...]

    # defaults
    count_top_users: bool = False


Role = NamedTuple(
    'Role', [
        ('name', str),
        ('id', int),
        ('role_type', Role_Type),
    ]
)

ChatBot = NamedTuple(
    'ChatBot', [
        ('name', str),
        ('id', int)
    ]
)

Command = NamedTuple(
    'Command', [
        ('name', str),
        ('description', str),
        ('function', Callable)
    ]
)
