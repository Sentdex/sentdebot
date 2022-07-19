from sqlalchemy import create_engine, BigInteger
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql, sqlite

from config import config
from util.logger import setup_custom_logger

logger = setup_custom_logger(__name__)

class Database:
  def __init__(self):
    if config.db.connect_string is None or config.db.connect_string == "":
      logger.error("Database connect string is empty!")
      exit(-1)

    try:
      self.base = declarative_base()
      self.db = create_engine(config.db.connect_string)

    except Exception as e:
      logger.error(f"Failed to create database connection\n{e}")
      exit(-1)

    logger.info("Database opened")

try:
  database:Database = Database()
  session:Session = sessionmaker(database.db)()
except Exception as e:
  logger.error(f"Failed to create database session\n{e}")
  exit(-1)

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')