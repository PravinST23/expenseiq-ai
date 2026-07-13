"""
Expense Approval API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.approval import ApprovalCreate
from app.schemas.approval import ApprovalResponse
from app.schemas.approval import ApprovalUpdate
from app.services.approval_service import approval_service

router = APIRouter(
    prefix="/approvals",
    tags=["Approvals"],
)


@router.post(
    "/",
    response_model=ApprovalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Approval",
)
def create_approval(
    approval: ApprovalCreate,
    db: Session = Depends(get_db),
):

    return approval_service.create_approval(
        db,
        approval,
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
):

    approval_service.delete_approval(
        db,
        approval_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )