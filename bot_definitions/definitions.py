from typing import NamedTuple, Literal, Callable

# module to define definitions for other modules Only

Channel = NamedTuple('Channel', [
    ('name', str),
    ('id', int),
    ('type', Literal['text', 'voice']),
    ('tags', tuple[Literal['community', 'general', 'help', 'image'], ...])])

Role = NamedTuple('Role', [
    ('name', str),
    ('id', int),
    ('type', Literal['admin', 'mod', 'vanity'])
])

ChatBot = NamedTuple('ChatBot', [
    ('name', str),
    ('id', int)
])

Command = NamedTuple('Command', [
    ('name', str),
    ('description', str),
    ('function', Callable)
])

