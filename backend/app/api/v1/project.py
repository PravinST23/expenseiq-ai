"""
Project API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.project import ProjectCreate
from app.schemas.project import ProjectResponse
from app.schemas.project import ProjectUpdate
from app.services.project_service import project_service

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
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


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Get Project By ID",
)
def get_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):

    return project_service.get_by_id(
        db,
        project_id,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update Project",
)
def update_project(
    project_id: UUID,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
):

    return project_service.update_project(
        db,
        project_id,
        project,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Project",
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):

    project_service.delete_project(
        db,
        project_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )