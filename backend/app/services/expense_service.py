"""
Expense Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.models.expense import Expense
from app.repositories.expense_repository import expense_repository
from app.schemas.expense import ExpenseCreate
from app.schemas.expense import ExpenseUpdate
from app.schemas.expense import ReimbursementUpdate

# Reimbursement state machine - only forward transitions allowed.
REIMBURSEMENT_TRANSITIONS = {
    "PENDING": {"APPROVED", "PAID"},
    "APPROVED": {"PAID"},
    "PAID": set(),
}


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

    def update_reimbursement(
        self,
        db: Session,
        expense_id: UUID,
        reimbursement_update: ReimbursementUpdate,
        current_employee: Employee | None = None,
    ):
        """
        Advance an expense's reimbursement state
        (PENDING -> APPROVED -> PAID). Only forward transitions
        are allowed, and an expense must be Approved before its
        reimbursement can be marked PAID.

        `processed_by` is taken from the authenticated employee
        when the call came through the HTTP API (always true - see
        require_roles on the route), ignoring whatever the request
        body claimed; falls back to the body's value for trusted
        internal callers (seed scripts) that bypass auth.
        """

        processed_by = (
            current_employee.full_name
            if current_employee is not None
            else reimbursement_update.processed_by
        )

        if not processed_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="processed_by is required.",
            )

        expense = self.get_by_id(
            db,
            expense_id,
        )

        if expense.status != "Approved":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "Reimbursement cannot be updated until the "
                    "expense is fully Approved."
                ),
            )

        target_state = reimbursement_update.reimbursement_state

        allowed = REIMBURSEMENT_TRANSITIONS.get(
            expense.reimbursement_state,
            set(),
        )

        if target_state not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Cannot move reimbursement from "
                    f"{expense.reimbursement_state} to "
                    f"{target_state}."
                ),
            )

        expense.reimbursement_state = target_state
        expense.reimbursement_updated_at = datetime.utcnow()
        expense.reimbursement_processed_by = processed_by

        return expense_repository.update(
            db,
            expense,
        )


expense_service = ExpenseService()