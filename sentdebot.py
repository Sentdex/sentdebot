import traceback
import disnake
from disnake import AllowedMentions, Intents, Game, Status
from disnake.ext import commands

from config import config
from util.logger import setup_custom_logger
from database.database_manipulation import init_tables
from util import general_util
from static_data.strings import Strings

logger = setup_custom_logger(__name__)

if config.base.discord_api_key is None:
  logger.error("Discord API key is missing!")
  exit(-1)

# Init database tables
init_tables()

intents = Intents.none()
intents.guilds = True
intents.members = True
intents.emojis = True
intents.messages = True
intents.message_content = True
intents.reactions = True
intents.presences = True
intents.typing = True
intents.voice_states = True

bot = commands.Bot(
  command_prefix=commands.when_mentioned_or(config.base.command_prefix + "."),
  help_command=None,
  case_insensitive=True,
  allowed_mentions=AllowedMentions(roles=False, everyone=False, users=True),
  intents=intents,
  sync_commands=True,
  max_messages=config.essentials.max_cached_messages
)

is_initialized = False

@bot.event
async def on_ready():
  global is_initialized
  if is_initialized:
    return
  is_initialized = True

  logger.info('Logged in as: {0} (ID: {0.id})'.format(bot.user))
  await bot.change_presence(activity=Game(name=config.base.status_message, type=0), status=Status.online)
  logger.info('Ready!')

@bot.event
async def on_message(message: disnake.Message):
  if not message.author.bot:
    if message.content.startswith(config.base.command_prefix + "."):
      orig_content = message.content

      # logger.info(f"Command content: {orig_content}")

      try:
        arg_start = message.content.find("(")
        if not message.content.endswith(")"):
          raise SyntaxError

        command_name = message.content[message.content.find(".") + 1:arg_start]
        args_string = message.content[arg_start+1:-1]

        args = []
        arg = ""
        in_parentheses = None
        in_codeblock = False
        for ch in args_string:
          if ch == "`" and in_parentheses is None:
            in_codeblock = not in_codeblock
            if not in_codeblock and arg != "":
              args.append(f"```{arg.strip()}```")
              arg = ""
            continue
          elif ch in ("\"", "\'") and not in_codeblock:
            if in_parentheses is None:
              if arg != "":
                raise SyntaxError

              in_parentheses = ch
              continue
            elif ch == in_parentheses:
              in_parentheses = None
              continue
          elif ch == "," and in_parentheses is None:
            args.append(f"\"{arg.strip()}\"")
            arg = ""
            continue
          arg += ch
        if arg != "":
          args.append(f"\"{arg.strip()}\"")

        # logger.info(f"Command name: `{command_name}`, Args: {args}, Number of args: {len(args)}")
        message.content = f"{config.base.command_prefix}.{command_name} {' '.join(args)}"

        # logger.info(f"New content: `{message.content}`")

        await bot.process_commands(message)
      except SyntaxError:
        await general_util.generate_error_message(message, Strings.error_command_syntax_error)
      finally:
        message.content = orig_content

for cog in config.cogs.protected:
  try:
    bot.load_extension(f"cogs.{cog}")
    logger.info(f"{cog} loaded")
  except:
    output = traceback.format_exc()
    logger.error(f"Failed to load {cog} module\n{output}")
    exit(-2)
logger.info("Protected modules loaded")

for cog in config.cogs.defaul_loaded:
  try:
    bot.load_extension(f"cogs.{cog}")
    logger.info(f"{cog} loaded")
  except:
    output = traceback.format_exc()
    logger.warning(f"Failed to load {cog} module\n{output}")
logger.info("Defaul modules loaded")

bot.run(config.base.discord_api_key)
