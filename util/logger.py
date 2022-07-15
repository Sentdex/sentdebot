import logging
import coloredlogs
from config import config

logging.getLogger('discord').setLevel(logging.WARNING)
logging.getLogger('asyncio').setLevel(logging.CRITICAL)

formater = logging.Formatter(fmt="%(asctime)s %(name)s %(levelname)s %(message)s", datefmt='%d-%m-%Y %H:%M:%S')

if config.log_to_file:
	fh = logging.FileHandler("discord.log")
	fh.setLevel(logging.WARNING)
	fh.setFormatter(formater)

def setup_custom_logger(name, override_log_level=None):
	logger = logging.getLogger(name)
	if config.log_to_file:
		logger.addHandler(fh)

	if not override_log_level:
		coloredlogs.install(level="INFO", logger=logger)
	else:
		coloredlogs.install(level=override_log_level, logger=logger)

	return logger