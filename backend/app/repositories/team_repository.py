"""
Team Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.team import Team
from app.repositories.base_repository import BaseRepository


class TeamRepository(BaseRepository[Team]):
    """
    Repository for Team (MAC) operations.
    """

    def __init__(self):
        super().__init__(Team)

    def get_by_team_code(
        self,
        db: Session,
        team_code: str,
    ):
        return (
            db.query(Team)
            .filter(Team.team_code == team_code)
            .first()
        )

    def get_by_id(
        self,
        db: Session,
        team_id: UUID,
    ):
        return (
            db.query(Team)
            .filter(Team.id == team_id)
            .first()
        )

    def update(
        self,
        db: Session,
        team: Team,
    ):
        db.commit()
        db.refresh(team)
        return team

    def delete(
        self,
        db: Session,
        team: Team,
    ):
        db.delete(team)
        db.commit()


team_repository = TeamRepository()
