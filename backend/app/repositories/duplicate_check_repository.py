"""
Duplicate Check Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.duplicate_check import DuplicateCheck
from app.repositories.base_repository import BaseRepository


class DuplicateCheckRepository(BaseRepository[DuplicateCheck]):
    """
    Repository for Duplicate Check operations.
    """

    def __init__(self):
        super().__init__(DuplicateCheck)

    def get_by_expense_id(
        self,
        db: Session,
        expense_id,
    ):
        return (
            db.query(DuplicateCheck)
            .filter(DuplicateCheck.expense_id == expense_id)
            .first()
        )


duplicate_check_repository = DuplicateCheckRepository()