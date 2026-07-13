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

from app.api.deps import get_db
from app.schemas.expense import ExpenseCreate
from app.schemas.expense import ExpenseResponse
from app.schemas.expense import ExpenseUpdate
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
)
def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
):

    return expense_service.create_expense(
        db,
        expense,
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