"""
Project Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.project import Project
from app.repositories.project_repository import project_repository
from app.schemas.project import ProjectCreate
from app.schemas.project import ProjectUpdate


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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Project Code already exists.",
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

    def get_by_id(
        self,
        db: Session,
        project_id: UUID,
    ):

        project = project_repository.get_by_id(
            db,
            project_id,
        )

        if project is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found.",
            )

        return project

    def update_project(
        self,
        db: Session,
        project_id: UUID,
        project_update: ProjectUpdate,
    ):

        project = self.get_by_id(
            db,
            project_id,
        )

        update_data = project_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(project, key, value)

        return project_repository.update(
            db,
            project,
        )

    def delete_project(
        self,
        db: Session,
        project_id: UUID,
    ):

        project = self.get_by_id(
            db,
            project_id,
        )

        project_repository.delete(
            db,
            project,
        )


project_service = ProjectService()