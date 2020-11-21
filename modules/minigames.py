import numpy as np
import asyncio
import random

from .permissions import is_called_in_bot_channel, is_priv
from .definitions import bot
from .decorators import advanced_perm_check_function, advanced_args_function


@bot.command(aliases=['sweeper', 'minesweeper'])
# @advanced_args_function(bot)
@advanced_perm_check_function(is_called_in_bot_channel, is_priv)
async def mines(ctx, *args, **kwargs):
    """
    Generates sweeper game, !sweeper (size) (bombs)
    Args:
        ctx:
        *args:

    Returns:

    """
    if len(args) == 0:
        size = 7
        bombs = None
    elif len(args) == 1:
        size = args[0]
        size = int(size)
        bombs = None
    elif len(args) == 2:
        size, bombs = args
        size = int(size)
        bombs = int(bombs)
    else:
        size = 7
        bombs = None

    "Check table size, 2k characters limit"
    if size < 1:
        size = 2
    elif size > 14:
        size = 14

    "Check bomb amount"
    fields = size * size
    if bombs is None or bombs < 0:
        bombs = size * size // 3.5
    elif bombs >= fields:
        bombs = fields - 1

    bomb_list = [1 if fi < bombs else 0 for fi in range(fields)]
    random.shuffle(bomb_list)
    temp_arr = np.array(bomb_list).reshape(size, size)
    bomb_arr = np.zeros((size + 2, size + 2), dtype=int)
    for rind, row in enumerate(temp_arr):
        rind += 1
        for cin, num in enumerate(row):
            cin += 1
            if num:
                bomb_arr[rind - 1:rind + 2, cin - 1:cin + 2] += 1
        await asyncio.sleep(0.01)

    bomb_arr = bomb_arr[1:-1, 1:-1]
    mask = temp_arr == 1
    bomb_arr[mask] = -1
    hidden_text = '\n'.join(
            "".join(f"||`{num:^2}`||" if num >= 0 else f"||`{'X':^2}`||" for num in row)
            for row in bomb_arr)
    text = f"Sweeper {size}x{size}, bombs: {bombs:.0f}  ({bombs / fields * 100:.0f}%)"
    sweeper_text = f"{text}\n{hidden_text}"
    message = await ctx.send(sweeper_text)
    return message