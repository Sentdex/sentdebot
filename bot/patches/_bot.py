import asyncio
from functools import partial

from discord.ext.commands import Context, Bot, AutoShardedBot

from .compatibility import clean_string

__all__ = (
    "ViewInjectingContext",
    "SnekBot",
    "AutoShardedSnekBot"
)

class ViewInjectingContext(Context):
    """A context class which modifies the View

    This class modifies the attribute named view,
    such that view's buffer and end are that of the cleaned string
    and not of message.content.

    In a way, this partially reinitializes the view.
    """

    async def _compat(self) -> 'ViewInjectingContext':
        # Execute our cleaner in an async manner.
        cleaned_buffer = await asyncio.get_event_loop().run_in_executor(None, partial(clean_string, self.message.content))
        self.view.buffer = cleaned_buffer
        self.end = len(cleaned_buffer)
        return self


# _Patch Should Not be used directly
class _Patch:
    """The Refactored patch class

    WARNING
    =======
    Do not use directly. Use the subclassed versions, :class:`SnekBot` and :class:`AutoShardedSnekBot` instead.
    """
    async def get_context(self, message, *, cls=ViewInjectingContext) -> Context:
        inst = await super().get_context(message, cls=cls) # type: ignore
        if cls is ViewInjectingContext:
            inst = await inst._compat()
        return inst

class SnekBot(_Patch, Bot):
    """Subclass of :class:`discord.ext.commands.Bot` but uses sentdebot styled commands"""
    pass

class AutoShardedSnekBot(_Patch, AutoShardedBot):
    """Subclass of :class:`discord.ext.commands.AutoShardedBot` but uses sentdebot styled commands"""
    pass

# These are only the patches so nothing fancy here
