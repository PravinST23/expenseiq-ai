"""
Expense Approval Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.approval import ExpenseApproval
from app.repositories.base_repository import BaseRepository


class ApprovalRepository(
    BaseRepository[ExpenseApproval]
):
    """
    Repository for Approval operations.
    """

    def __init__(self):
        super().__init__(ExpenseApproval)

    def get_by_id(
        self,
        db: Session,
        approval_id: UUID,
    ):
        return (
            db.query(ExpenseApproval)
            .filter(
                ExpenseApproval.id == approval_id
            )
            .first()
        )

    def get_by_expense(
        self,
        db: Session,
        expense_id: UUID,
    ):
        return (
            db.query(ExpenseApproval)
            .filter(
                ExpenseApproval.expense_id == expense_id
            )
            .all()
        )

    def update(
        self,
        db: Session,
        approval: ExpenseApproval,
    ):
        db.commit()
        db.refresh(approval)
        return approval

    def delete(
        self,
        db: Session,
        approval: ExpenseApproval,
    ):
        db.delete(approval)
        db.commit()


approval_repository = ApprovalRepository()