from sqlalchemy import Column, String

from database import database, BigIntegerType

class QuestionAndAnswer(database.base):
  __tablename__ = "questions_and_answers"

  id = Column(BigIntegerType, primary_key=True, unique=True, index=True, autoincrement=True)

  question = Column(String, nullable=False, index=True, unique=True)
  answer = Column(String, nullable=False)
