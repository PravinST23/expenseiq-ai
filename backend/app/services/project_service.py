"""
Project Service
"""

from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate


class ProjectService:

    def create_project(
        self,
        db: Session,
        project: ProjectCreate,
    ):

        existing = project_repository.get_by_project_code(
            db,
            project.project_code,
        )

        if existing:
            raise ValueError(
                "Project Code already exists."
            )

        new_project = Project(
            **project.model_dump()
        )

        return project_repository.create(
            db,
            new_project,
        )

    def get_all(
        self,
        db: Session,
    ):
        return project_repository.get_all(db)


project_service = ProjectService()