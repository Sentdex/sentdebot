"""Cog to randomly assign vanity roles"""
import random
import nextcord as discord
from nextcord.ext import commands, tasks

from bot_config import BotConfig

config = BotConfig.get_config('sentdebot')

blocked_attachment_extensions = ['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff', 'svg']

class RoleLottery(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # on ready
    @commands.Cog.listener()
    async def on_ready(self):
        # go through the bot configs and get all of the roles tagged with vanity
        roles = [r for r in config.roles if r.role_type == 'vanity']
        # now, check to see if the guild has all of the roles by id, if not, by name, if not, create
        guild = self.bot.get_guild(config.guild_id)
        for role in roles:
            if not guild.get_role(role.id):
                if not discord.utils.get(guild.roles, name=role.name):
                    # random color
                    # with hoise
                    role_color = discord.Color(random.randint(0, 0xFFFFFF))
                    await guild.create_role(name=role.name, color=role_color, hoist=True)

    # on message
    @commands.Cog.listener()
    async def on_message(self, message):
        # todo still bugged
        author_roles = [r.name for r in message.author.roles]
        vanity_roles = [r.id for r in config.roles if r.role_type == 'vanity']
        guild = self.bot.get_guild(config.guild_id)
        if random.choice(range(1)) == 1:
            matches = [r for r in author_roles if r.id in vanity_roles]
            if len(matches) == 0:
                try:
                    role_id_choice = random.choice(vanity_roles)
                    actual_role_choice = guild.get_role(role_id_choice)
                    if actual_role_choice is None:
                        actual_role_choice = discord.utils.get(guild.roles, id=role_id_choice)
                        if actual_role_choice is None:
                            # random colour
                            actual_role_choice = await guild.create_role(
                                name=config.roles[role_id_choice].name,
                                colour=discord.Colour(
                                    random.randint(0, 0xFFFFFF)
                                ),
                                hoist=True,
                            )
                            await message.author.add_roles(actual_role_choice)
                    author_roles.append(actual_role_choice)
                    await message.author.edit(roles=author_roles)
                except Exception as e:
                    print('EDITING ROLES ISSUE:', str(e))
        # if message author does not have a vanity role and they are posting an image, block them
        if len(author_roles) == 0:
            # if the message has image attachemnts, remove them from the message
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    if attachment.filename.split('.')[-1] in blocked_attachment_extensions:
                        await attachment.delete()



def setup(bot):
    bot.add_cog(RoleLottery(bot))
