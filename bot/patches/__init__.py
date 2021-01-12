"""This Package contains patches

The patches in this package allow us to transform
SentdeBot Commands into a string which
discord.ext.commands needs.
"""

# I could have just written a new commands lib,
# but,
#   1. That is too time consuming and hard to maintain
#   2. discord.ext.commands has a lot of useful features
#       and many libs depend on commands.Bot
#
# hence I have decided to make a light compatibility layer
from ._bot import *
from .compatibility import clean_string