"""
Compliance Check API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.compliance_check import ComplianceCheckResponse
from app.services.compliance_check_service import (
    compliance_check_service,
)

router = APIRouter(
    prefix="/compliance-checks",
    tags=["Compliance Checks"],
)


@router.get(
    "/",
    response_model=list[ComplianceCheckResponse],
    summary="Get Compliance Checks",
)
def get_compliance_checks(
    db: Session = Depends(get_db),
):

    return compliance_check_service.get_all(db)


@router.get(
    "/expense/{expense_id}",
    response_model=ComplianceCheckResponse,
    summary="Get Compliance Check By Expense",
)
def get_compliance_check_by_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    from fastapi import HTTPException
    from fastapi import status

    check = compliance_check_service.get_by_expense(
        db,
        expense_id,
    )

    if check is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No compliance check found for this expense.",
        )

    return check
