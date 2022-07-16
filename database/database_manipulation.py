from database import session, database

from database.tables import user_metrics
from database.tables import message_metrics
from database.tables import projects
from database.tables import help_threads

from util.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

def init_tables():
  database.base.metadata.create_all(database.db)
  session.commit()

  logger.info("Initializating all loaded tables")