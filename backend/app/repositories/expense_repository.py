"""
Expense Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

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

    def get_by_id(
        self,
        db: Session,
        expense_id: UUID,
    ):
        return (
            db.query(Expense)
            .filter(Expense.id == expense_id)
            .first()
        )

    def update(
        self,
        db: Session,
        expense: Expense,
    ):
        db.commit()
        db.refresh(expense)
        return expense

    def delete(
        self,
        db: Session,
        expense: Expense,
    ):
        db.delete(expense)
        db.commit()


expense_repository = ExpenseRepository()