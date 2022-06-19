# I am going to refactor into a class so we can use dependency injection to expand and test the bot, will remove a
# lot of rewriting later


# same imports from the original class

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import asyncio
import discord
import pandas as pd
import random
import numpy as np
import time
import os
import re

# py -3.6 -m pip install --upgrade requests-html
from requests_html import HTMLSession
from collections import Counter
from matplotlib import style

from bot_definitions import *


# a refactoring of sentdebot.py.OLD into a class

class Bot(discord.Client):
    # here want the core bot object, with parameters for the dependency injection
    #  for the roles, channels, commands and bots
    # it may be worthwhile making a coimmand handler class for injection too,
    # just so we can swap them out and see what works best without complete rewrites,
    # also, by breaking the code into smaller, more readable pieces, we may actually encourage
    # other folks to help expand it, not many folks will wanna touch it while it is as fragile as it is
    # right now.
    def __init__(self, token, intents, roles, channels, commands, bots, message_handler):
        pass
