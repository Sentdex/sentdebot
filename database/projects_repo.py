from typing import Optional, List

from database import session
from database.tables.projects import Project

def get_by_name(name: str) -> Optional[Project]:
  return session.query(Project).filter(Project.name == name).one_or_none()

def add_project(project_name: str, project_description: str) -> Optional[Project]:
  if get_by_name(project_name) is None:
    item = Project(name=project_name, description=project_description)
    session.add(item)
    session.commit()
    return item
  return None

def remove_project(project_name: str) -> bool:
  project = get_by_name(project_name)
  if project is None:
    return False

  session.delete(project)
  session.commit()
  return True

def get_all() -> List[Project]:
  return session.query(Project).all()
