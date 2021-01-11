"""This is the package which contains all the cogs"""
from .community import Community
from .logs import Logs
from .misc import Cmds
from .sudo import Sudo


# Yes this entire package will be one extension
# This will speed up the launch!
def setup(bot):
    bot.add_cog(Community(bot))
    bot.add_cog(Logs(bot))
    bot.add_cog(Cmds())
    bot.add_cog(Sudo(bot))
