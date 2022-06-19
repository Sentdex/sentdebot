path = '/sentdebot/'

# days of history to work with
DAYS_BACK = 21
RESAMPLE = "60min"

# when doing counters of activity, top n users.
MOST_COMMON_INT = 10
# names of channels where we want to count activity.
COMMUNITY_BASED_CHANNELS = [
    "__main__",
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
    "politics_enter_at_own_risk"
]

HELP_CHANNELS = [
    "help",
    "hello_technical_questions",
    "help_0",
    "help_1",
    "help_2",
    "help_3",
    "help_overflow"
]

DISCORD_BG_COLOR = '#36393E'

token = open(f"{path}/token.txt", "r").read().split('\n')[0]

admins_mods_ids = admin_id, mod_id = 405506750654054401, 405520180974714891

chatbots = (
    405511726050574336,
    428904098985803776,
    414630095911780353,
    500507500962119681
)

vanity_role_ids = [
    479433667576332289,
    501115401577431050,
    501115079572324352,
    501114732057460748,
    501115820273958912,
    501114928854204431,
    479433212561719296
]

channel_ids = [
    408713676095488000,  # main
    412620789133606914  # help
]

image_chan_ids = [
    408713676095488000,
    412620789133606914,
    476412789184004096,
    499945870473691146,
    484406428233367562,
]
