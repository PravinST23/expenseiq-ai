"""
Expense API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.expense import ExpenseCreate
from app.schemas.expense import ExpenseResponse
from app.services.expense_service import expense_service

router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"],
)


@router.post(
    "/",
    response_model=ExpenseResponse,
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