import discord
import asyncio
import random
import time
import re

from .permissions import CommandWithoutPermissions
from .definitions import send_disapprove, send_approve

from discord.ext.commands import CommandError
from discord import HTTPException, NotFound


def approve_fun(coro):
    """
    Decorator that adds reaction if success, else x.
    Args:
        coro:

    Returns:
        message object returned by calling given function with given params
    """

    async def decorator(ctx, *args, **kwargs):
        try:
            result = await coro(ctx, *args, **kwargs)
            await send_approve(ctx)
            return result
        except NotFound:
            pass
        except Exception as pe:
            try:
                await send_disapprove(ctx)
            except NotFound:
                pass
            raise pe

    decorator.__name__ = coro.__name__
    decorator.__doc__ = coro.__doc__
    return decorator


def _check_advanced_perm(ctx, *args, rule_sets=None, restrictions=None, **kwargs):
    if not rule_sets and not restrictions:
        raise CommandWithoutPermissions("Not checking any permission")

    if restrictions:
        if type(restrictions) is not list and type(restrictions) is not tuple:
            restrictions = [restrictions]

        for rule in restrictions:
            valid, error = rule(ctx, *args, **kwargs)
            if not valid:
                raise error

    rule_sets = [rules if (type(rules) is list or type(rules) is set) else [rules]
                 for rules in rule_sets]
    all_errors = []

    for rules in rule_sets:
        valids, errors = zip(*[chk_f(ctx, *args, **kwargs) for chk_f in rules])
        if all(valids):
            return True
        else:
            all_errors += errors

    if len(all_errors) > 0:
        raise all_errors[0]
    else:
        return True


def advanced_perm_check_function(*rules_sets, restrictions=None):
    """
    Check channels and permissions, use -s -sudo or -a -admin to run it.
    Args:
        *rules_sets: list of rules, 1d or 2d,
        restrictions: Restrictions must be always met
    Returns:
        message object returned by calling given function with given params
    """

    def decorator(coro):
        async def f(ctx, *args, **kwargs):
            valid = _check_advanced_perm(ctx,
                                         *args,
                                         **kwargs,
                                         rule_sets=[*rules_sets], restrictions=restrictions)
            if valid:
                output = await coro(ctx, *args, **kwargs)
                return output
            else:
                # logger.error(f"Permission check failed! Exceptions should be raised earlier!")
                raise CommandError("Permission check failed.")

        f.__name__ = coro.__name__
        f.__doc__ = coro.__doc__
        return f

    return decorator


def advanced_args_function(bot, bold_name=False):
    """
    Decorator that translates args to create flags and converts string into kwargs.
    Args:
        bot: bot instance
        bold_name:

    Returns:
        message object returned by calling given function with given params
    """

    def wrapper(coro):
        # logger.warning(f"Advanced args are not supporting non kwargs functions")

        async def f(ctx, *args, **kwargs):
            # if text:
            #     logger.error(f"Text is already in advanced args: {text}")

            good_args, kwargs = _get_advanced_args(bot, ctx, *args, bold_name=bold_name, **kwargs)
            output = await coro(ctx, *good_args, **kwargs)
            return output

        f.__name__ = coro.__name__
        f.__doc__ = coro.__doc__
        return f

    return wrapper


def _get_advanced_args(bot, ctx, *args, bold_name=False, **kwargs):
    if not kwargs:
        kwargs = {}

    good_args = list()
    text_args = []
    args, kwargs = _get_advanced_kwargs(bot, ctx, *args, **kwargs, bold_name=bold_name)
    args = list(args)

    for arg in args:
        if arg:
            if ',' in arg:
                arg, *rest = arg.split(',')
                for _rest in rest:
                    args.append(_rest)
            good_args.append(arg)
            text_args.append(arg)
        # else:
        #     logger.debug(f"Unwanted arg: '{arg}'")

    good_args = tuple(_ar for _ar in good_args if _ar)
    print(good_args)
    return good_args, kwargs


def _get_advanced_kwargs(bot, ctx, *args, bold_name=False, **kwargs):
    args = list(args)
    if not kwargs:
        # kwargs = {"force": False, "dry": False, "sudo": False, 'update': False}
        kwargs = {}

    good_args = list()
    mention_pattern = re.compile(r"<@[!&]\d+>")
    text_args = []

    for arg in args:
        # if arg.startswith("-f") or arg == 'force':
        #     "force, enforce parameters"
        #     kwargs['force'] = True
        # elif arg.startswith("-d") or arg == 'dry':
        #     "dry run"
        #     kwargs['dry'] = True
        # elif arg.startswith("-u") or arg == 'update' or arg == "upgrade":
        #     "update"
        #     kwargs['update'] = True
        # elif arg.startswith("-s") or arg.startswith("-a") or arg == 'sudo':
        #     "sudo or admin"
        #     kwargs['sudo'] = True
        # elif arg.startswith("-"):
        #     try:
        #         _ = float(arg)
        #         good_args.append(arg)
        #     except ValueError:
        #         "drop unknown parameters"
        #         # logger.warning(f"unknown argument: {arg}")
        if "=" in arg:
            key, val = arg.split("=")
            if key == "force" or key == "dry":
                continue
            if key and val:
                kwargs.update({key: val})
        elif mention_pattern.match(arg) or "@everyone" in arg or "@here" in arg:
            name = string_mention_converter(bot, ctx.guild, arg, bold_name=bold_name)
            text_args.append(name)

        else:
            good_args.append(arg)
            text_args.append(arg)

    good_args = tuple(good_args)
    text = ' '.join(text_args)
    kwargs['text'] = text

    return good_args, kwargs


def string_mention_converter(bot, guild, text: "input str", bold_name=True) -> "String":
    user_pattern = re.compile(r"<@!(\d+)>")
    role_pattern = re.compile(r"<@&(\d+)>")
    new_text = text

    new_text = new_text.replace("@everyone", "<everyone>")
    new_text = new_text.replace("@here", "<here>")

    user_list = user_pattern.findall(text)
    role_list = role_pattern.findall(text)

    for user in user_list:
        try:
            user_name = bot.get_user(int(user)).name
        except AttributeError:
            user_name = f"{user}"
        if bold_name:
            new_text = new_text.replace(f"<@!{user}>", f"@**{user_name}**")
        else:
            new_text = new_text.replace(f"<@!{user}>", f"@{user_name}")

    for role in role_list:
        try:
            roleid = int(role)
            role_name = guild.get_role(roleid).name
        except AttributeError as err:
            # logger.error(f"Error in string_mention_converter {err}")
            role_name = f"{role}"
        new_text = new_text.replace(f"<@&{role}>", f"@*{role_name}*")
    return new_text
