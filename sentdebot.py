import traceback
import disnake
from disnake import AllowedMentions, Intents, Game, Status
from disnake.ext import commands
import ast

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

def parse(message):
  root = ast.parse(message)
  match root:
    case ast.Module(
      body=[
        ast.Expr(
          value=ast.Call(
            func=ast.Attribute(
              value=ast.Name(id=config.base.command_prefix),
              attr=method
            ),
            args=positional
          )
        )
      ]
    ):
      for i, pos in enumerate(positional):
        if isinstance(pos, ast.Constant):
          positional[i] = pos.value
        elif isinstance(pos, ast.Name):
          positional[i] = pos.id
        else:
          raise SyntaxError

      return method, positional

@bot.event
async def on_message(message: disnake.Message):
  if not message.author.bot:
    if message.content.startswith(config.base.command_prefix + "."):
      orig_content = message.content
      try:
        method, args = parse(message.content)
        # logger.info(f"Command {method}, Args: {args}")

        message.content = f"{config.base.command_prefix}.{method} {' '.join(args)}"
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
