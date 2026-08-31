"""
Expense Approval Service

Author: Pravin Shanmugavel
Project: ExpenseIQ

Enforces the manager-chain approval routing computed by
app.workflow.manager_chain: Reporting Manager -> Skip-Level Manager
-> CFO, resolved per the EXPENSE'S REQUESTER (not a generic role).
An approval action is only valid when performed by the specific
employee that chain resolves to at the expense's current level;
once recorded, the workflow either advances the expense to the next
required level or, if this was the last required level, finalizes
the approval and moves the claim into the reimbursement pipeline.
"""

from datetime import datetime
from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.approval import ExpenseApproval
from app.models.employee import Employee
from app.models.expense import Expense
from app.repositories.approval_repository import approval_repository
from app.schemas.approval import ApprovalCreate
from app.schemas.approval import ApprovalUpdate
from app.workflow.manager_chain import level_label
from app.workflow.manager_chain import resolve_approver

VALID_ACTIONS = {"Approved", "Rejected"}


class ApprovalService:
    """
    Business logic for Expense Approval.
    """

    def create_approval(
        self,
        db: Session,
        approval: ApprovalCreate,
        current_employee: Employee,
    ):
        """
        current_employee is the authenticated caller - the source of
        truth for WHO is acting. They must be the exact employee the
        manager chain resolves to for this expense's requester at
        its current level (e.g. the requester's actual Reporting
        Manager for level 1) - not just anyone holding a broad role.
        """

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

        if approval.action not in VALID_ACTIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Invalid action '{approval.action}'. "
                    f"Must be one of {sorted(VALID_ACTIONS)}."
                ),
            )

        if expense.status in ("Approved", "Rejected"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Expense is already {expense.status} - "
                    "no further approval actions allowed."
                ),
            )

        resolved = resolve_approver(
            db,
            expense.employee,
            expense.current_approval_level,
        )

        if resolved.employee.id != current_employee.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"This expense is currently awaiting action from "
                    f"its {resolved.label} "
                    f"({resolved.employee.full_name}), not you."
                ),
            )

        new_approval = ExpenseApproval(
            expense_id=approval.expense_id,
            approver_employee_id=current_employee.id,
            approver_role=resolved.label,
            approval_level=resolved.level,
            approver_name=current_employee.full_name,
            action=approval.action,
            comments=approval.comments,
        )

        db.add(new_approval)

        if approval.action == "Rejected":

            expense.status = "Rejected"

        else:

            if (
                expense.current_approval_level
                < expense.required_approval_level
            ):

                expense.current_approval_level += 1

                next_label = level_label(
                    expense.current_approval_level
                )

                expense.status = (
                    f"Pending {next_label} Approval"
                )

            else:

                expense.status = "Approved"
                expense.reimbursement_state = "APPROVED"
                expense.reimbursement_updated_at = (
                    datetime.utcnow()
                )
                expense.reimbursement_processed_by = (
                    current_employee.full_name
                )

        db.commit()

        db.refresh(new_approval)

        return new_approval

    def get_pending_for_employee(
        self,
        db: Session,
        employee: Employee,
    ) -> list[Expense]:
        """
        Every non-terminal expense currently awaiting THIS
        employee's action - resolved per-requester via the manager
        chain, not by a fixed role/level. Powers the manager
        dashboard's approval queue.
        """

        pending = []

        candidates = (
            db.query(Expense)
            .filter(~Expense.status.in_(("Approved", "Rejected")))
            .all()
        )

        for expense in candidates:

            try:
                resolved = resolve_approver(
                    db,
                    expense.employee,
                    expense.current_approval_level,
                )
            except Exception:
                continue

            if resolved.employee.id == employee.id:
                pending.append(expense)

        return pending

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
