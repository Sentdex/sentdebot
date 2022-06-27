# cog to collect user metrics and store them to a db
import os

from nextcord.ext import commands

import sqlite3
import datetime
import time


class UserMetrics(commands.Cog):
    # we need to collect several metrics:
    #   * user stats over time (active, inactive, etc)
    #   * message frequency over time
    #   * top users per channel
    #   * top users per category
    #   * top users per server
    #   * individual user stats


    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(UserMetrics(bot))
