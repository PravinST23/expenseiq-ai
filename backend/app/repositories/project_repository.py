"""
Project Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.base_repository import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Repository for Project operations.
    """

    def __init__(self):
        super().__init__(Project)

    def get_by_project_code(
        self,
        db: Session,
        project_code: str,
    ):
        return (
            db.query(Project)
            .filter(Project.project_code == project_code)
            .first()
        )


project_repository = ProjectRepository()