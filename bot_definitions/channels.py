from definitions import Channel

# module to hold definitions and functions pertaining to Discord channels ONLY

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

def get_all_by_tag(tag: str) -> list:
    return [channel for channel in channels if tag in channel.tags]

def get_all_by_type(channel_type: str) -> list:
    return [channel for channel in channels if channel.channel_type == channel_type]
