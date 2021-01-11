import logging
from typing import Set
from discord import Intents
import pathlib

from .patches import SnekBot

logger = logging.getLogger(__name__)

commands_available = """```py
def commands():
    return {
        sentdebot.member_count(): 'get member count',
        sentdebot.community_report(): 'get some stats on community',
        sentdebot.search("QUERY"): 'search for a string',
        sentdebot.commands(): 'get commands',
        sentdebot.logout(): 'Sentdex-only command to log Sentdebot off'
        sentdebot.user_activity(): 'See some stats on top users',
    }
```"""

# Why are we using 1.5 :
#   <https://discordpy.readthedocs.io/en/latest/intents.html#i-don-t-like-this-can-i-go-back>

# Why do we need intents:
#   <https://discordpy.readthedocs.io/en/latest/intents.html#>
def get_intents() -> Intents:
    intents = Intents.all()
    intents.typing = False
    intents.dm_reactions = False
    # intents.reactions = False
    # Sentdebot NEEDS MEMBERS PRIVILEGED INTENT
    # intents.members = True
    # intents.presences = True
    return intents

# This is the class where we introduce new features
class SentdeBot(SnekBot):
    """Inherits from discord.ext.commands.Bot

    Uses A.b(arg1, arg2, ...) style of commands where
    A is the prefix
    """
    # TODO:: [May be let these ids be shelved and modified during runtime?
    #         aka let the ids be changed by commands]

    vanity_roles: Set[int] = {
        479433667576332289,
        501115401577431050,
        501115079572324352,
        501114732057460748,
        501115820273958912,
        501114928854204431,
        479433212561719296
    }

    admin_id: int = 405506750654054401
    mod_id: int = 405520180974714891

    privileged_roles: Set[int] = {admin_id, mod_id}

    channels: Set[int] = {
        408713676095488000,  # main
        412620789133606914   # help
    }

    image_channels: Set[int]= {
        408713676095488000,
        412620789133606914,
        476412789184004096,
        499945870473691146,
        484406428233367562,
    }

    guild_id = 405403391410438165 # Sentdex (server)

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
        "help_overflow"
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

    def __init__(self, *a, **kw) -> None:
        self.guild = None
        self.path = kw.get("file_path", pathlib.Path(__file__).parent / "files")

        # Convert to pathlib.Path or Fail
        try:
            self.path = pathlib.Path(self.path)
        except TypeError as err:
            pass

        self.path.mkdir(exist_ok=True)
        self.path = self.path.resolve()
        self.DAYS_BACK = kw.get("days_back", 21)
        self.RESAMPLE = kw.get("resample", "60min")
        self.MOST_COMMON_INT = kw.get("top_users", 10)
        super().__init__(*a, **kw)
        self.load_extension("cogs")

    async def on_ready(self):
        logger.info("SentDeBot is up and running!")
        self.guild = self.get_guild(SentdeBot.guild_id)

    @property
    def cmds(self) -> str:
        return commands_available

#logging.basicConfig(format="%(asctime)s %(name)s:%(levelname)s: %(message)s", level=logging.INFO, datefmt="[%a, %d %B %Y %X]")