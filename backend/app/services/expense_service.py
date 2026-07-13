"""
Expense Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.expense import Expense
from app.repositories.expense_repository import expense_repository
from app.schemas.expense import ExpenseCreate
from app.schemas.expense import ExpenseUpdate


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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Expense Number already exists.",
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

    def get_by_id(
        self,
        db: Session,
        expense_id: UUID,
    ):

        expense = expense_repository.get_by_id(
            db,
            expense_id,
        )

        if expense is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found.",
            )

        return expense

    def update_expense(
        self,
        db: Session,
        expense_id: UUID,
        expense_update: ExpenseUpdate,
    ):

        expense = self.get_by_id(
            db,
            expense_id,
        )

        update_data = expense_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                expense,
                key,
                value,
            )

        return expense_repository.update(
            db,
            expense,
        )

    def delete_expense(
        self,
        db: Session,
        expense_id: UUID,
    ):

        expense = self.get_by_id(
            db,
            expense_id,
        )

        expense_repository.delete(
            db,
            expense,
        )


expense_service = ExpenseService()