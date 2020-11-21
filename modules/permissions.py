from .definitions import SENTDEX_ID, DHAN_ID, HELLO_CHARLES_CH_ID


class RestrictedError(PermissionError):
    pass


class CommandWithoutPermissions(PermissionError):
    pass


def is_admin(ctx, *args, **kwargs):
    if ctx.message.author.id in [SENTDEX_ID, DHAN_ID]:
        return True, None
    else:
        return False, RestrictedError("This command is restricted to Youshisu.")


def is_priv(ctx, *args, **kwargs):
    if ctx.guild:
        return False, RestrictedError("This command is restricted to private channels.")
    else:
        return True, None


def is_not_priv(ctx, *args, **kwargs):
    if ctx.guild:
        return True, None
    else:
        return False, RestrictedError("This command is restricted to server channels.")


def is_called_in_bot_channel(ctx, *args, **kwargs):
    if ctx.channel.id == HELLO_CHARLES_CH_ID:
        return True, None
    else:
        return False, RestrictedError("This command is restricted to channel 'hello-charles'.")
