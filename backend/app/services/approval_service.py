"""
Expense Approval Service

Author: Pravin Shanmugavel
Project: ExpenseIQ

Enforces the 3-role (L1 Manager / L2 Finance / L3 CFO) approval
routing computed by the Smart Auto-Approval Engine. An approval
action is only valid at the expense's current routing level; once
recorded, the workflow either advances the expense to the next
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
from app.workflow.approval_workflow import LEVEL_LABELS
from app.workflow.approval_workflow import ROLE_LEVELS
from app.workflow.approval_workflow import approval_workflow

VALID_ACTIONS = {"Approved", "Rejected"}


class ApprovalService:
    """
    Business logic for Expense Approval.
    """

    def create_approval(
        self,
        db: Session,
        approval: ApprovalCreate,
        current_employee: Employee | None = None,
    ):
        """
        current_employee, when provided (always true for the
        authenticated HTTP route - see app.api.v1.approval), is the
        source of truth for WHO is acting and at WHAT role: it
        overrides whatever approver_role/approver_name the request
        body carried, so a caller cannot forge an approval as a
        role/person they aren't. Internal trusted callers (e.g.
        scripts/seed_demo_data.py, which drives the service layer
        directly rather than over HTTP) may omit it and fall back to
        the body's fields.
        """

        if current_employee is not None:
            approval = approval.model_copy(
                update={
                    "approver_role": current_employee.role,
                    "approver_name": current_employee.full_name,
                }
            )

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

        role_level = ROLE_LEVELS.get(approval.approver_role)

        if role_level is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Unknown approver_role "
                    f"'{approval.approver_role}'. Must be one "
                    f"of {sorted(ROLE_LEVELS)}."
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

        if role_level != expense.current_approval_level:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "This expense is currently awaiting "
                    f"{LEVEL_LABELS[expense.current_approval_level]} "
                    f"action, not {LEVEL_LABELS[role_level]}."
                ),
            )

        new_approval = ExpenseApproval(
            expense_id=approval.expense_id,
            approver_role=approval.approver_role,
            approval_level=role_level,
            approver_name=approval.approver_name,
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

                next_label = LEVEL_LABELS[
                    expense.current_approval_level
                ]

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
                    approval.approver_name
                )

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
