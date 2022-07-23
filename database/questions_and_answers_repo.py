from typing import List, Tuple, Optional

from database import session
from database.tables.questions_and_answers import QuestionAndAnswer

def find_question(question: str) -> Optional[QuestionAndAnswer]:
  return session.query(QuestionAndAnswer).filter(QuestionAndAnswer.question == question).one_or_none()

def create_question_and_answer(question: str, answer: str) -> Optional[QuestionAndAnswer]:
  if find_question(question) is not None:
    return None

  item = QuestionAndAnswer(question=question, answer=answer)
  session.add(item)
  session.commit()
  return item

def get_all_questions() -> List[Tuple[int, str]]:
  data = session.query(QuestionAndAnswer.id, QuestionAndAnswer.question).all()
  return [(d[0], d[1]) for d in data]

def get_answer_by_id(ans_id: int) -> Optional[str]:
  data = session.query(QuestionAndAnswer.answer).filter(QuestionAndAnswer.id == ans_id).one_or_none()
  return str(data[0]) if data is not None else None

def get_all() -> List[Tuple[str, str]]:
  data = session.query(QuestionAndAnswer.question, QuestionAndAnswer.answer).all()
  return [(d[0], d[1]) for d in data]

def remove_question(question: str):
  session.query(QuestionAndAnswer).filter(QuestionAndAnswer.question == question).delete()
  session.commit()
