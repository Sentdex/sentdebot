from discord.ext.commands import Context, Bot

from .compatibility import clean_string

__all__ = (
    "ViewInjectingContext",
    "SnekBot"
)

class ViewInjectingContext(Context):
    """A context class which modifies the View

    This class modifies the attribute named view,
    such that view's buffer and end are that of the cleaned string
    and not of message.content.

    In a way, this partially reinitializes the view.
    """
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        cleaned_buffer = clean_string(self.message.content)
        self.view.buffer = cleaned_buffer
        self.end = len(cleaned_buffer)

# Forgive Me,  I remembered the bot's Pfp so i named it Snek
class SnekBot(Bot):
    def __init__(self, *args, **options):
        super.__init__(*args, **options)

    async def get_context(self, message, *, cls=ViewInjectingContext):
        return await super().get_context(message, cls=cls)

# These are only the patches so nothing fancy here
