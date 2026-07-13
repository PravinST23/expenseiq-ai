"""
Project API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.project import ProjectCreate
from app.schemas.project import ProjectResponse
from app.services.project_service import project_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    summary="Create Project",
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
):

    return project_service.create_project(
        db,
        project,
    )


@router.get(
    "/",
    response_model=list[ProjectResponse],
    summary="Get Projects",
)
def get_projects(
    db: Session = Depends(get_db),
):

    return project_service.get_all(db)