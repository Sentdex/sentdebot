import traceback
import asyncio
import discord
import random
import time
import os
import re

# py -3.6 -m pip install --upgrade requests-html
from requests_html import HTMLSession
from matplotlib import style
from discord.ext.commands import CommandError
from discord import Embed, Colour

from .definitions import bot, local_files_path, HELLO_TEXTS
from .definitions import SENTDEX_ID, SENTEX_GUILD_ID
from .definitions import MAIN_CH_ID, IMAGE_CHAN_IDS, VANITY_ROLE_IDS, CHATBOTS

from .permissions import is_called_in_bot_channel, is_priv, is_not_priv, is_admin
from .decorators import advanced_perm_check_function, advanced_args_function

from .background_tasks import community_report
from .minigames import mines
from .emojis import EMOJIS, HAPPY_FACES

style.use("dark_background")

commands_available = """```py
def commands():
    return {
        sentdebot.member_count(): 'get member count',
        sentdebot.community_report(): 'get some stats on community',
        sentdebot.search("QUERY"): 'search for a string',
        sentdebot.commands(): 'get commands',
        sentdebot.logout(): 'Sentdex-only command to log Sentdebot off'
        sentdebot.user_activity(): 'See some stats on top users',
    }
```"""


def search_term(message):
    try:
        match = re.fullmatch('sentdebot.search\((["|\'])([^\)]+)(["|\'])\)', message)
        if match.group(1) != match.group(3):
            return False
        for check in re.finditer(match.group(1), match.group(2)):
            if match.group(2)[check.start() - 1] != '\\':
                return False
        return match.group(2)
    except Exception:
        return False


@bot.event  # event decorator/wrapper
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('help(sentdebot)'))


@bot.event
async def on_message(message):
    print(f"{message.channel}: {message.author}: {message.author.name}: {message.content}")
    sentdex_guild = bot.get_guild(SENTEX_GUILD_ID)

    # print(author_roles)
    # author_role_ids = [r.id for r in author_roles]

    if random.choice(range(500)) == 30:
        try:
            author_roles = message.author.roles
            matches = [r for r in author_roles if r.id in VANITY_ROLE_IDS]
            # print(matches)

            if len(matches) == 0:
                try:
                    role_id_choice = random.choice(VANITY_ROLE_IDS)
                    actual_role_choice = sentdex_guild.get_role(role_id_choice)
                    # print(type(message.author))
                    author_roles.append(actual_role_choice)
                    await message.author.edit(roles=author_roles)
                except Exception as e:
                    print('EDITING ROLES ISSUE:', str(e))
        except Exception:
            pass
    with open(os.path.join(local_files_path, 'msgs.csv'), "a") as f:
        if message.author.id not in CHATBOTS:
            f.write(f"{int(time.time())}, {message.author.id}, {message.channel}\n")

    with open(os.path.join(local_files_path, 'log.csv'), "a") as f:
        if message.author.id not in CHATBOTS:
            try:
                f.write(f"{int(time.time())}, {message.author.id}, {message.channel}, {message.content}\n")
            except Exception as e:
                f.write(f"{str(e)}\n")

    if "sentdebot.member_count()" == message.content.lower():
        await message.channel.send(f"```py\n{sentdex_guild.member_count}```")

    elif "sentdebot.community_report()" == message.content.lower() and message.channel.id in IMAGE_CHAN_IDS:
        online, idle, offline = community_report(sentdex_guild)

        file = discord.File(os.path.join(local_files_path, "online.png"), filename=f"online.png")
        await message.channel.send("", file=file)

        await message.channel.send(
                f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    elif "sentdebot.p6()" == message.content.lower():
        await message.channel.send(f"```\nThe Neural Networks from Scratch videos will resume one day. https://nnfs.io```")

    elif "sentdebot.user_activity()" == message.content.lower() and message.channel.id in IMAGE_CHAN_IDS:  # and len([r for r in author_roles if r.id in admins_mods_ids]) > 0:
        file = discord.File(os.path.join(local_files_path, "activity.png"), filename=f"activity.png")
        await message.channel.send("", file=file)

        # await message.channel.send(f'```py\n{{\n\t"Online": {online},\n\t"Idle/busy/dnd": {idle},\n\t"Offline": {offline}\n}}```')

    elif "help(sentdebot)" == message.content.lower() or "sentdebot.commands()" == message.content.lower():
        await message.channel.send(commands_available)

    # if it doesnt work later.
    # elif "sentdebot.logout()" == message.content.lower() and message.author.id == 324953561416859658:
    elif "sentdebot.logout()" == message.content.lower() and message.author.id == SENTDEX_ID:
        await bot.close()

    elif "sentdebot.gtfo()" == message.content.lower() and message.author.id == SENTDEX_ID:
        await bot.close()

    elif "sentdebot.get_history()" == message.content.lower() and message.author.id == SENTDEX_ID:

        channel = sentdex_guild.get_channel(MAIN_CH_ID)

        async for message in channel.history(limit=999999999999999):
            if message.author.id == SENTDEX_ID:
                with open(os.path.join(local_files_path, "history_out.csv"), "a") as f:
                    f.write(f"{message.created_at},1\n")

    elif message.content.lower().startswith("sentdebot.search"):
        query = search_term(message.content)
        print(f"Query: {query}")
        if query:
            # query = match.group(1)
            print(query)

            qsearch = query.replace(" ", "%20")
            full_link = f"https://pythonprogramming.net/search/?q={qsearch}"
            session = HTMLSession()
            r = session.get(full_link)

            specific_tutorials = [(tut.text, list(tut.links)[0]) for tut in r.html.find("a") if
                                  "collection-item" in tut.html]

            if len(specific_tutorials) > 0:
                return_str = "\n---------------------------------------\n".join(
                        f'{tut[0]}: <https://pythonprogramming.net{tut[1]}>' for tut in specific_tutorials[:3])
                return_str = f"```Searching for '{query}'```\n" + return_str + f"\n----\n...More results: <{full_link}>"

                await message.channel.send(return_str)
            else:
                await message.channel.send(f"""```py
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
NotFoundError: {query} not found```""")

    elif bot.user in message.mentions and not message.content.startswith("!"):
        ch = message.channel
        text = random.choice(HELLO_TEXTS)
        emote = random.choice(HAPPY_FACES)
        await ch.send(text.format(message.author.name, emote=emote))
    else:
        await bot.process_commands(message)


async def get_last_message(channel_id, user_id, limit=10):
    channel = bot.get_channel(channel_id)
    messages = await channel.history(limit=limit).flatten()
    message = None
    for msg in messages:
        if msg.author.id == user_id:
            message = msg
            break
    return message


@bot.event
async def on_command_error(ctx, command_error):
    text = ctx.message.content
    invoked = ctx.invoked_with
    text_error = str(command_error)
    server = "private_message" if not ctx.guild else f"{ctx.guild} ({ctx.guild.id})"

    if text_error.startswith("The check functions for command") or text_error.startswith("No permission"):
        # logger.warning(f"No permission: '{text}', server: '{server}'")
        emoji = "⛔"
        await ctx.channel.send(f"Some permissions do not allow it to run here, '{text_error}' '!{invoked}'",
                               delete_after=30)

    elif text_error.endswith("is not found"):
        # logger.warning(f"Command not found: '{text}', server: '{server}'")
        emoji = "❓"

    elif text_error.startswith("Command raised an exception: RestrictedError"):
        # logger.warning(f"Restricted usage: '{text}', server: '{server}'")
        emoji = "⛔"
        await ctx.channel.send(f"{command_error.original} '!{invoked}'", delete_after=30)

    elif text_error.startswith("Command raised an exception: CommandWithoutPermissions"):
        # logger.error(f"Command is free to all users: '{text}', server: '{server}'")
        emoji = "⛔"
        await ctx.channel.send(f"Command is not checking any permissions, sorry. '!{invoked}'", delete_after=30)

    elif text_error.startswith("You are missing"):
        # logger.warning(f"Missing permission: '{text_error}', server: '{server}'")
        emoji = "❌"
        await ctx.channel.send(f"{text_error} '!{invoked}'", delete_after=30)

    elif text_error.startswith("Command raised an exception: Forbidden: 403 Forbidden"):
        # logger.warning(f"Bot is missing permissions: '{text_error}', server: '{server}', '!{invoked}'")
        emoji = "❌"
        await ctx.channel.send(f"Bot is missing permissions: '!{invoked}'", delete_after=30)

    elif text_error.startswith("Command raised an exception: NotImplementedError"):
        # logger.warning(f"Not implemented feature: '{text_error}', server: '{server}', '!{invoked}'")
        emoji = "❌"
        await ctx.channel.send(f"Not implemented feature: '{text}'", delete_after=30)

    elif type(command_error) is CommandError:
        # logger.warning(f"Command error: '{text_error}', server: '{server}', '!{invoked}'")
        emoji = "❌"
        await ctx.channel.send(f"{text_error}: '!{invoked}'")

    elif "required positional argument" in text_error:
        emoji = "❌"
        await ctx.channel.send(f"Some arguments are missing: '{command_error.original}'", delete_after=30)

    else:
        tb_text = traceback.format_exception(type(command_error), command_error, command_error.__traceback__)
        tb_text = ''.join([line for line in tb_text if f'bot{os.path.sep}' in line or f'app{os.path.sep}' in line])
        emoji = "❌"
        # logger.error(
        #         f"No reaction for this error type:\n"
        #         f"Command: '{ctx.message.content}', server: '{server}', \n"
        #         f"'{command_error}'\n"
        #         f"Partial traceback:\n{tb_text}")
        print(
                f"No reaction for this error type:\n"
                f"Command: '{ctx.message.content}', server: '{server}', \n"
                f"'{command_error}'\n"
                f"Partial traceback:\n{tb_text}")

    try:
        await ctx.message.add_reaction(emoji=emoji)
    except Exception:
        pass


@bot.command()
@advanced_args_function(bot)
# @log_call_function
@advanced_perm_check_function(is_not_priv)
# @my_help.help_decorator("Poll with maximum 10 answers. Minimum 2 answers, maximum 10. timeout is optional",
#                         "<question>? <ans1>, ..., <ans10> (timeout=<sec>)")
async def poll(ctx, *args, text, force=False, dry=False, timeout=3 * 60, **kwargs):
    """
    Multi choice poll with maximum 10 answers
    Example `!poll Question, answer1, answer2, .... answer10`
    Available delimiters: . ; ,
    You can add more time with `timeout=200`, default 180, maximum is 3600 (1hour)
    Use `-d` for dryrun
    Args:
        ctx:
        *args:
        dry:
        **kwargs:

    Returns:

    """

    # text = ' '.join(args)
    # logger.debug(text)
    arr_text = re.split(r"['.?;,]", text)
    arr_text = [el.lstrip().rstrip() for el in arr_text if len(el) > 0]
    poll_color = Colour.from_rgb(250, 165, 0)
    finished_poll_color = Colour.from_rgb(30, 255, 0)

    timeout = float(timeout)
    if timeout > 60 * 60 and not force:
        timeout = 60 * 60

    update_interval = 30 if 30 < timeout else timeout

    if len(arr_text) < 3:
        await ctx.send(f"Got less than 1 questions and 2 answers, use some delimiter ?;,")
        return None

    question, *answers = arr_text
    question = question.title() + "?"

    if dry:
        text = f"Question: {question}\n" + f"Answers {len(answers)}: {answers}\n" + f"Timeout: {timeout}"
        await ctx.send(text)
        return None

    elif len(answers) > 10:
        confirm_message = await ctx.send(
                f"Got more than 10 answers, sorry. If you want poll with 10 answers, press reaction.",
                delete_after=60)
        await confirm_message.add_reaction(EMOJIS["green_ok"])

        def wait_for_confirm(reaction, _cur_user):
            return str(reaction.emoji) == EMOJIS["green_ok"] \
                   and _cur_user.id == ctx.author.id \
                   and reaction.message.id == confirm_message.id

        try:
            reaction, user = await bot.wait_for("reaction_add", check=wait_for_confirm, timeout=60)
            answers = answers[0:10]
            await confirm_message.delete()
        except asyncio.TimeoutError:
            return None
    try:
        await ctx.message.delete()
    except Exception:
        pass

    answer_dict = {}

    embed = Embed(title=question, colour=poll_color)
    embed.set_author(name=ctx.author.name)
    embed.set_thumbnail(url=ctx.author.avatar_url)
    embed.set_footer(text=f"Time left: {timeout / 60:4.1f} min")

    for num, ans in enumerate(answers, 1):
        emoji = EMOJIS[num]
        answer_dict[emoji] = {'ans': ans.title(), 'votes': 0}
        embed.add_field(name=emoji, value=ans, inline=False)

    poll = await ctx.send(embed=embed)

    await poll.add_reaction("🛑")
    for num in range(1, len(answers) + 1):
        await poll.add_reaction(EMOJIS[num])
        await asyncio.sleep(0.01)

    def check_end_reaction(reaction, user):
        b1 = reaction.emoji == "🛑"
        b2 = reaction.message.id == poll.id
        b3 = user == ctx.message.author
        return b1 and b2 and b3

    end_time = time.time() + timeout
    while time.time() <= end_time:
        end_loop = False
        try:
            reaction, message = await bot.wait_for('reaction_add', check=check_end_reaction, timeout=update_interval)
            end_loop = True
        except asyncio.TimeoutError as err:
            pass

        poll = await ctx.channel.fetch_message(poll.id)
        # all_votes = 0
        all_users = []
        vote_emojis = [EMOJIS[num] for num in range(1, 11)]
        for rc in poll.reactions:
            if rc.emoji not in vote_emojis:
                continue
            users = [user async for user in rc.users()]
            all_users += users
            me = rc.me
            count = rc.count - 1 if me else 0
            # all_votes += count
            answer_dict[rc.emoji]['votes'] = count

        all_users_count = len(set(all_users)) - 1
        embed = Embed(title=question, colour=poll_color)
        embed.set_author(name=ctx.author.name)
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.set_footer(text=f"Time left: {(end_time - time.time()) / 60:4.1f} min")
        for number in range(1, 11):
            try:
                emoji = EMOJIS[number]
                ans = answer_dict[emoji]['ans']
                votes = answer_dict[emoji]['votes']
                # fraction = votes / all_votes * 100 if all_votes > 0 else 0
                fraction = votes / all_users_count * 100 if all_users_count > 0 else 0
                embed.add_field(name=f"{emoji} -`{fraction:<3.1f} %`", value=ans, inline=False)
            except KeyError:
                break

        await poll.edit(embed=embed)
        await asyncio.sleep(0.01)
        if end_loop:
            break

    embed.colour = finished_poll_color
    embed.set_footer(text="")
    await poll.edit(content='🔒 Poll has ended', embed=embed)
    await poll.clear_reaction("🛑")


@bot.command(aliases=['nnfs.io', 'nfs', 'nn'])
async def nnfs(ctx, *args, **kwargs):
    color = Colour.from_rgb(10, 180, 50)
    url = r'https://nnfs.io/'
    desc = '"Neural Networks From Scratch" is a book intended to teach you how to build neural networks on your own, without any libraries, so you can better understand deep learning and how all of the elements work. This is so you can go out and do new/novel things with deep learning as well as to become more successful with even more basic models.'
    embed = Embed(title=f"Click link", colour=color, url=url, description=None)

    sentdex = bot.get_user(SENTDEX_ID)
    embed.set_thumbnail(url=sentdex.avatar_url)
    embed.add_field(name="NNFS is out!", value=desc)
    # embed.set_author(name="Sentdex")
    embed.set_footer(text=f"for {ctx.author.name}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=embed)
