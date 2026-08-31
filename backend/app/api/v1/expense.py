"""
Expense API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_current_employee
from app.api.deps import get_db
from app.api.deps import require_roles
from app.models.employee import Employee
from app.schemas.expense import ExpenseCreate
from app.schemas.expense import ExpenseResponse
from app.schemas.expense import ExpenseUpdate
from app.schemas.expense import ReimbursementUpdate
from app.services.approval_service import approval_service
from app.services.expense_service import expense_service

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Expense",
    description=(
        "Submits the claim as the authenticated employee - "
        "employee_id in the body is ignored/overridden."
    ),
)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):

    return expense_service.create_expense(
        db,
        expense,
        current_employee=current_employee,
    )


@router.get(
    "/",
    response_model=list[ExpenseResponse],
    summary="Get Expenses",
)
def get_expenses(
    db: Session = Depends(get_db),
):

    return expense_service.get_all(db)


@router.get(
    "/pending-for-me",
    response_model=list[ExpenseResponse],
    summary="Get Expenses Pending My Approval",
    description=(
        "Every non-terminal expense currently awaiting the "
        "authenticated employee's action, resolved per-requester "
        "via the manager chain (Reporting Manager -> Skip-Level "
        "Manager -> CFO) - not by a fixed role. Powers the manager "
        "dashboard's approval queue."
    ),
)
def get_pending_for_me(
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(get_current_employee),
):

    return approval_service.get_pending_for_employee(db, current_employee)


@router.get(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Get Expense By ID",
)
def get_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    return expense_service.get_by_id(
        db,
        expense_id,
    )


@router.put(
    "/{expense_id}",
    response_model=ExpenseResponse,
    summary="Update Expense",
)
def update_expense(
    expense_id: UUID,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
):

    return expense_service.update_expense(
        db,
        expense_id,
        expense,
    )


@router.delete(
    "/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Expense",
)
def delete_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    expense_service.delete_expense(
        db,
        expense_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


@router.patch(
    "/{expense_id}/reimbursement",
    response_model=ExpenseResponse,
    summary="Advance Reimbursement State",
    description="Protected - only the CFO can mark a claim's reimbursement as PAID.",
)
def update_reimbursement(
    expense_id: UUID,
    reimbursement: ReimbursementUpdate,
    db: Session = Depends(get_db),
    current_employee: Employee = Depends(require_roles("CFO")),
):

    return expense_service.update_reimbursement(
        db,
        expense_id,
        reimbursement,
        current_employee=current_employee,
    )