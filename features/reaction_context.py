import disnake
from disnake.ext.commands import Bot
from typing import Union, Optional

class ReactionContext:
    def __init__(self, channel: disnake.TextChannel, guild: Optional[disnake.Guild], author: Union[disnake.Member, disnake.User], message: disnake.Message, reply_to: Optional[disnake.Message], emoji: Union[disnake.Emoji, str]):
        self.channel = channel
        self.guild = guild
        self.author = author
        self.message = message
        self.reply_to = reply_to
        self.emoji = emoji

    @classmethod
    async def from_payload(cls, bot: Bot, payload: disnake.RawReactionActionEvent):
        channel = bot.get_channel(payload.channel_id)
        guild = None

        if channel is None:
            return None

        if hasattr(channel, "guild") is not None:
            if not isinstance(channel, disnake.TextChannel):
                return None
            guild = channel.guild

        author = payload.member if payload.member is not None else None

        if author is None and guild is not None:
            author = await guild.get_or_fetch_member(payload.user_id)

        if author is None:
            return None

        if author.bot:
            return None

        try:
            message: disnake.Message = await channel.fetch_message(payload.message_id)

            if message is None:
                return None
        except disnake.errors.NotFound:
            return None

        reply_to = None
        if message.reference is not None and message.reference.message_id is not None:
            try:
                reply_to = await channel.fetch_message(message.reference.message_id)
            except disnake.errors.NotFound:
                pass  # Reply is there optional.

        if payload.emoji.is_custom_emoji():
            emoji = bot.get_emoji(payload.emoji.id)
            if emoji is None:
                emoji = payload.emoji
        else:
            emoji = payload.emoji.name

        return cls(channel, guild, author, message, reply_to, emoji)
