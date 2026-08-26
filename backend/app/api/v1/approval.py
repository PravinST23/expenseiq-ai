"""
Expense Approval API

Author: Pravin Shanmugavel
Project: ExpenseIQ

Write endpoints are protected: only an authenticated employee
holding an approval role (L1_MANAGER / L2_FINANCE / L3_CFO) can
record or modify an approval action. See app.api.deps.require_roles
and ApprovalService.create_approval for how the JWT identity
overrides any approver_role/approver_name the request body carries.
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.deps import require_roles
from app.models.employee import Employee
from app.schemas.approval import ApprovalCreate
from app.schemas.approval import ApprovalResponse
from app.schemas.approval import ApprovalUpdate
from app.services.approval_service import approval_service

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)

APPROVER_ROLES = ("L1_MANAGER", "L2_FINANCE", "L3_CFO")


@router.post(
    "/",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Approval",
)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles(*APPROVER_ROLES)),
):

    return approval_service.create_approval(
        db,
        approval,
        current_employee=current_employee,
    )


@router.get(
    "/",
    response_model=list[ApprovalResponse],
    summary="Get Approvals",
)
def get_approvals(
    db: Session = Depends(get_db),
):

    return approval_service.get_all(db)


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
    summary="Get Approval By ID",
)
def get_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
):

    return approval_service.get_by_id(
        db,
        approval_id,
    )


@router.get(
    "/expense/{expense_id}",
    response_model=list[ApprovalResponse],
    summary="Get Approval History By Expense",
)
def get_approval_history(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    return approval_service.get_by_expense(
        db,
        expense_id,
    )


@router.put(
    "/{approval_id}",
    response_model=ApprovalResponse,
    summary="Update Approval",
)
def update_approval(
    approval_id: UUID,
    approval: ApprovalUpdate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles(*APPROVER_ROLES)),
):

    return approval_service.update_approval(
        db,
        approval_id,
        approval,
    )


@router.delete(
    "/{approval_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Approval",
)
def delete_approval(
    approval_id: UUID,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles(*APPROVER_ROLES)),
):

    approval_service.delete_approval(
        db,
        approval_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )
