import traceback
from disnake import AllowedMentions, Intents, Game, Status
from disnake.ext import commands

from config import config
from util.logger import setup_custom_logger
from database.database_manipulation import init_tables

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

bot = commands.Bot(
  command_prefix=commands.when_mentioned_or(*config.base.command_prefixes),
  help_command=None,
  case_insensitive=True,
  allowed_mentions=AllowedMentions(roles=False, everyone=False, users=True),
  intents=intents,
  sync_commands=True
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
