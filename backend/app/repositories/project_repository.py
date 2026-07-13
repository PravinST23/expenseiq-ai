"""
Project Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

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

    def get_by_id(
        self,
        db: Session,
        project_id: UUID,
    ):
        return (
            db.query(Project)
            .filter(Project.id == project_id)
            .first()
        )

    def update(
        self,
        db: Session,
        project: Project,
    ):
        db.commit()
        db.refresh(project)
        return project

    def delete(
        self,
        db: Session,
        project: Project,
    ):
        db.delete(project)
        db.commit()


project_repository = ProjectRepository()