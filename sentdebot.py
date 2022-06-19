import os
import discord
from discord.ext import commands, tasks
from bot_definitions import *
from bot_config import *

intents = discord.Intents.all()
print(intents)