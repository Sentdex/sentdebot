from definitions import Channel

# module to hold definitions and functions pertaining to Discord channels ONLY

channels = [
    Channel('__init__', 476473718479257620, 'text', ('community',)),

    Channel('__main__', 408713676095488000, 'text', ('general', 'community'), True),

    Channel('help', 412620789133606914, 'text', ('help', 'community'), True),
    Channel('help_0', 412620789133606914, 'text', ('help', 'community')),
    Channel('help_1', 507281643606638622, 'text', ('help', 'community')),
    Channel('help_2', 682674227664388146, 'text', ('help', 'community')),
    Channel('help_3', 843130901998469177, 'text', ('help', 'community')),

    Channel('voice-channel-text', 484406428233367562, 'text', ('general', 'community')),
    Channel('dogs', 671016601440747520, 'text', ('general', 'community')),
    Channel('show_and_tell', 767379896040161290, 'text', ('general', 'community')),
]

COMMUNITY_BASED_CHANNELS = [
    "__init__",
    "__main__",

    "help",
    "help_0",
    "help_1",
    "help_2",
    "help_3",

    "voice-channel-text",

    "dogs",

    "show_and_tell",

    "main",
    "politics_enter_at_own_risk"
    "hello_technical_questions",
    "help_overflow",
]
