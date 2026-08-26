"""
Duplicate Check API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.duplicate_check import DuplicateCheckResponse
from app.services.duplicate_check_service import (
    duplicate_check_service,
)

router = APIRouter(
    prefix="/duplicate-checks",
    tags=["Duplicate Checks"],
)


@router.get(
    "/",
    response_model=list[DuplicateCheckResponse],
    summary="Get Duplicate Checks",
)
def get_duplicate_checks(
    db: Session = Depends(get_db),
):

    return duplicate_check_service.get_all(db)


@router.get(
    "/expense/{expense_id}",
    response_model=DuplicateCheckResponse,
    summary="Get Duplicate Check By Expense",
)
def get_duplicate_check_by_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    check = duplicate_check_service.get_by_expense(
        db,
        expense_id,
    )

    if check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No duplicate check found for this expense.",
        )

    return check
