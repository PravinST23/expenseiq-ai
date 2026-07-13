"""
Expense Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories.base_repository import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """
    Repository for Expense operations.
    """

    def __init__(self):
        super().__init__(Expense)

    def get_by_expense_number(
        self,
        db: Session,
        expense_number: str,
    ):
        return (
            db.query(Expense)
            .filter(Expense.expense_number == expense_number)
            .first()
        )


expense_repository = ExpenseRepository()