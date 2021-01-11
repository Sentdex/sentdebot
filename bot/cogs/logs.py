import logging
import random
import time

import discord
from discord.ext.commands import Cog

class Logs(Cog):
    logger = logging.getLogger(f"<Cog 'Logs' at {__name__}>")

    def __init__(self, bot) -> None:
        self.bot = bot
        self.log = open(self.bot.path / "log.csv", "a")
        self.msgs = open(self.bot.path / "msgs.csv", "a")

    def cog_unload(self) -> None:
        self.log.close()
        self.msgs.close()

    @Cog.listener()
    async def on_message(self, message):
        print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
        # https://discordpy.readthedocs.io/en/latest/api.html#discord.Message.type
        # Dont Give member role on join.
        if message.type != discord.MessageType.new_member:
            # Dont mess with Global Random instance on join
            if random.choice(range(500)) == 30:
                author_roles = message.author.roles
                matches = [r for r in author_roles if r.id in self.bot.vanity_roles]
                #print(matches)

                if len(matches) == 0:
                    try:
                        role_id_choice = random.choice(self.bot.vanity_roles)
                        actual_role_choice = self.bot.guild.get_role(role_id_choice)
                        #print(type(message.author))
                        author_roles.append(actual_role_choice)
                        await message.author.edit(roles=author_roles)
                    except Exception as e:
                        self.logger.exception('EDITING ROLES ISSUE:')


        if not message.author.bot:
            self.msgs.write(f"{int(time.time())},{message.author.id},{message.channel}\n")

            try:
                self.log.write(f"{int(time.time())},{message.author.id},{message.channel},{message.content}\n")
            except Exception as e:
                self.log.write(f"{str(e)}\n")


def setup(bot):
    bot.add_cog(Logs(bot))
