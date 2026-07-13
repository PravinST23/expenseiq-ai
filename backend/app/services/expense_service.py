"""
Expense Service
"""

from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories.expense_repository import expense_repository
from app.schemas.expense import ExpenseCreate


class ExpenseService:

    def create_expense(
        self,
        db: Session,
        expense: ExpenseCreate,
    ):

        existing = expense_repository.get_by_expense_number(
            db,
            expense.expense_number,
        )

        if existing:
            raise ValueError(
                "Expense Number already exists."
            )

        new_expense = Expense(
            **expense.model_dump()
        )

        return expense_repository.create(
            db,
            new_expense,
        )

    def get_all(
        self,
        db: Session,
    ):
        return expense_repository.get_all(db)


expense_service = ExpenseService()