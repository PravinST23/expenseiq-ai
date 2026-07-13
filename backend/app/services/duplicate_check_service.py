"""
Duplicate Check Service
"""

from sqlalchemy.orm import Session

from app.models.duplicate_check import DuplicateCheck
from app.repositories.duplicate_check_repository import duplicate_check_repository
from app.schemas.duplicate_check import DuplicateCheckCreate


class DuplicateCheckService:

    def create(
        self,
        db: Session,
        duplicate: DuplicateCheckCreate,
    ):

        new_duplicate = DuplicateCheck(
            **duplicate.model_dump()
        )

        return duplicate_check_repository.create(
            db,
            new_duplicate,
        )


duplicate_check_service = DuplicateCheckService()