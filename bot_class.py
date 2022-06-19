# I am going to refactor into a class so we can use dependency injection to expand and test the bot, will remove a
# lot of rewriting later

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

from bot_definitions import Role, ChatBot, Command, Channel
from config import *


class Sentdebot:
    def __init__(
            self,
            roles: list[Role],
            channels: list[Channel],
            commands: list[Command],
            chatbots: list[ChatBot],
            bot_token=open(f"{path}/token.txt", "r").read().split('\n')[0],
            intents=discord.Intents.all()
    ):

        self.bot_token = bot_token
        self.roles = roles
        self.channels = channels
        self.commands = commands
        self.chatbots = chatbots
        self.intents = intents
        self.client = discord.Client(intents=self.intents)