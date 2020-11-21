import discord
import os

from discord.ext.commands import Bot

local_files_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'sentdebot'))

SENTEX_GUILD_ID = 405403391410438165
SENTDEX_ID = 324953561416859658
DHAN_ID = 150409781595602946
MAIN_CH_ID = 408713676095488000
DOGS_CH_ID = 671016601440747520
HELP_CH_ID_0 = 412620789133606914
HELP_CH_ID_1 = 507281643606638622
HELP_CH_ID_2 = 682674227664388146
VOICE2TEXT_CH_ID = 484406428233367562
HELLO_CHARLES_CH_ID = 407958260168130570

IMAGE_CHAN_IDS = [MAIN_CH_ID,
                  HELP_CH_ID_0,
                  HELP_CH_ID_1,
                  HELP_CH_ID_2,
                  476412789184004096,  # ?
                  499945870473691146,  # ?
                  VOICE2TEXT_CH_ID,
                  ]

CHATBOTS = [405511726050574336,  # Charles
            428904098985803776,  # Irene
            414630095911780353,  # Charlene (Charles' alter ego)
            500507500962119681]  # ?

SENTDEBOT_ID = 499921685051342848

admin_id = 405506750654054401
mod_id = 405520180974714891

admins_mods_ids = [admin_id, mod_id]
# condition to restrict a command to admins/mods: len([r for r in author_roles if r.id in admins_mods_ids]) > 0

VANITY_ROLE_IDS = [479433667576332289,
                   501115401577431050,
                   501115079572324352,
                   501114732057460748,
                   501115820273958912,
                   501114928854204431,
                   479433212561719296]

MOST_COMMON_INT = 10  # when doing counters of activity, top n users.
DAYS_BACK = 21  # days of history to work with
RESAMPLE = "60min"

# names of channels where we want to count activity.
COMMUNITY_BASED_CHANNELS = ["__main__",
                            "main",
                            "help",
                            "help_0",
                            "help_1",
                            "help_2",
                            "help_3",
                            "voice-channel-text",
                            "__init__",
                            "hello_technical_questions",
                            "help_overflow",
                            "dogs",
                            "show_and_tell",
                            "politics_enter_at_own_risk"]

HELP_CHANNELS = ["help",
                 "hello_technical_questions",
                 "help_0",
                 "help_1",
                 "help_2",
                 "help_3",
                 "help_overflow"]

DISCORD_BG_COLOR = '#36393E'

HELLO_TEXTS = ["Hello there {emote} {0}.",
               "How is it going today {0}? {emote}",
               "What's up {0}?", "Hey {0}. {emote}",
               "Hi {0}, do you feel well today? {emote}",
               "Good day {0}. {emote}",
               "Oh {0}! Hello. {emote}",
               "Hey {emote}. {0}",
               "Hey, do you want some coffee {0}? {emote}",
               ]

intents = discord.Intents.all()
bot = Bot(command_prefix="!", ignore_case=True, intents=intents)


async def send_approve(ctx):
    await ctx.message.add_reaction('✅')


async def send_disapprove(ctx):
    await ctx.message.add_reaction('❌')
