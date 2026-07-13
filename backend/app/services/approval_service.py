"""
Expense Approval Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.approval import ExpenseApproval
from app.models.expense import Expense
from app.repositories.approval_repository import approval_repository
from app.schemas.approval import ApprovalCreate
from app.schemas.approval import ApprovalUpdate


class ApprovalService:
    """
    Business logic for Expense Approval.
    """

    def create_approval(
        self,
        db: Session,
        approval: ApprovalCreate,
    ):

        expense = (
            db.query(Expense)
            .filter(
                Expense.id == approval.expense_id
            )
            .first()
        )

        if expense is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found.",
            )

        new_approval = ExpenseApproval(
            **approval.model_dump()
        )

        db.add(new_approval)

        if approval.approver_role == "Manager":

            if approval.action == "Approved":
                expense.status = "Manager Approved"
            else:
                expense.status = "Manager Rejected"

        elif approval.approver_role == "Finance":

            if approval.action == "Approved":
                expense.status = "Completed"
            else:
                expense.status = "Finance Rejected"

        db.commit()

        db.refresh(new_approval)

        return new_approval

    def get_all(
        self,
        db: Session,
    ):
        return approval_repository.get_all(db)

    def get_by_id(
        self,
        db: Session,
        approval_id: UUID,
    ):

        approval = approval_repository.get_by_id(
            db,
            approval_id,
        )

        if approval is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Approval not found.",
            )

        return approval

    def get_by_expense(
        self,
        db: Session,
        expense_id: UUID,
    ):
        return approval_repository.get_by_expense(
            db,
            expense_id,
        )

    def update_approval(
        self,
        db: Session,
        approval_id: UUID,
        approval_update: ApprovalUpdate,
    ):

        approval = self.get_by_id(
            db,
            approval_id,
        )

        update_data = approval_update.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                approval,
                key,
                value,
            )

        return approval_repository.update(
            db,
            approval,
        )

    def delete_approval(
        self,
        db: Session,
        approval_id: UUID,
    ):

        approval = self.get_by_id(
            db,
            approval_id,
        )

        approval_repository.delete(
            db,
            approval,
        )


approval_service = ApprovalService()