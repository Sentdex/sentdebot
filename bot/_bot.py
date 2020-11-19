from typing import Set
from discord import Intents

from .patches import SnekBot
from .utils import RoleId, ChannelId

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

    vanity_roles: Set[RoleId] = {
        479433667576332289,
        501115401577431050,
        501115079572324352,
        501114732057460748,
        501115820273958912,
        501114928854204431,
        479433212561719296
    }

    admin_id: RoleId = 405506750654054401
    mod_id: RoleId = 405520180974714891

    privileged_roles: Set[RoleId] = {admin_id, mod_id}

    channel: Set[ChannelId] = {
        408713676095488000,  # main
        412620789133606914   # help
    }

    image_channels: Set[ChannelId]= {
        408713676095488000,
        412620789133606914,
        476412789184004096,
        499945870473691146,
        484406428233367562,
    }

    guild_id = 405403391410438165 # Sentdex (server)

    def __init__(self, *a, **kw) -> None:
        super().__init__(*a, **kw)

    async def on_ready(self):
        print("SentDeBot is up and running!")
        self.guild = self.get_guild(SentdeBot.guild_id)