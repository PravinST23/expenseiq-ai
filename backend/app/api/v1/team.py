"""
Team (MAC) API

Author: Pravin Shanmugavel
Project: ExpenseIQ

Reads are open (needed for the sign-up form's team picker); writes
are HR_HEAD only.
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps import require_roles
from app.models.employee import Employee
from app.schemas.team import TeamCreate
from app.schemas.team import TeamResponse
from app.schemas.team import TeamUpdate
from app.services.team_service import team_service

router = APIRouter(
    prefix="/teams",
    tags=["Teams"],
)


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Team",
    description="HR_HEAD only.",
)
def create_team(
    team: TeamCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles("HR_HEAD")),
):

    return team_service.create_team(db, team)


@router.get(
    "/",
    response_model=list[TeamResponse],
    summary="Get Teams",
)
def get_teams(db: Session = Depends(get_db)):

    return team_service.get_all(db)


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Get Team By ID",
)
def get_team(team_id: UUID, db: Session = Depends(get_db)):

    return team_service.get_by_id(db, team_id)


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Update Team",
    description="HR_HEAD only.",
)
def update_team(
    team_id: UUID,
    team: TeamUpdate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles("HR_HEAD")),
):

    return team_service.update_team(db, team_id, team)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Team",
    description="HR_HEAD only.",
)
def delete_team(
    team_id: UUID,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles("HR_HEAD")),
):

    team_service.delete_team(db, team_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
