"""
Team (MAC) Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.team import Team
from app.repositories.team_repository import team_repository
from app.schemas.team import TeamCreate
from app.schemas.team import TeamUpdate


class TeamService:

    def create_team(
        self,
        db: Session,
        team: TeamCreate,
    ):

        existing = team_repository.get_by_team_code(
            db,
            team.team_code,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Team Code already exists.",
            )

        new_team = Team(**team.model_dump())

        return team_repository.create(db, new_team)

    def get_all(self, db: Session):
        return team_repository.get_all(db)

    def get_by_id(self, db: Session, team_id: UUID):

        team = team_repository.get_by_id(db, team_id)

        if team is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found.",
            )

        return team

    def update_team(
        self,
        db: Session,
        team_id: UUID,
        team_update: TeamUpdate,
    ):

        team = self.get_by_id(db, team_id)

        update_data = team_update.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(team, key, value)

        return team_repository.update(db, team)

    def delete_team(self, db: Session, team_id: UUID):

        team = self.get_by_id(db, team_id)

        team_repository.delete(db, team)


team_service = TeamService()
