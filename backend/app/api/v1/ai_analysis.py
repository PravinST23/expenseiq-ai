"""
Expense AI Analysis API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.ai_analysis import AIAnalysisResponse
from app.services.ai_analysis_service import (
    ai_analysis_service,
)

router = APIRouter(
    prefix="/ai-analysis",
    tags=["AI Analysis"],
)


# ---------------------------------------------------------
# Get All AI Analysis
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[AIAnalysisResponse],
    summary="Get All AI Analysis",
)
def get_all_analysis(
    db: Session = Depends(get_db),
):

    return ai_analysis_service.get_all(
        db,
    )


# ---------------------------------------------------------
# Get AI Analysis By ID
# ---------------------------------------------------------

@router.get(
    "/{analysis_id}",
    response_model=AIAnalysisResponse,
    summary="Get AI Analysis By ID",
)
def get_analysis_by_id(
    analysis_id: UUID,
    db: Session = Depends(get_db),
):

    return ai_analysis_service.get_by_id(
        db,
        analysis_id,
    )


# ---------------------------------------------------------
# Get AI Analysis By Receipt
# ---------------------------------------------------------

@router.get(
    "/receipt/{receipt_id}",
    response_model=AIAnalysisResponse,
    summary="Get AI Analysis By Receipt",
)
def get_analysis_by_receipt(
    receipt_id: UUID,
    db: Session = Depends(get_db),
):

    return ai_analysis_service.get_by_receipt(
        db,
        receipt_id,
    )


# ---------------------------------------------------------
# Get AI Analysis By Expense
# ---------------------------------------------------------

@router.get(
    "/expense/{expense_id}",
    response_model=list[AIAnalysisResponse],
    summary="Get AI Analysis By Expense",
)
def get_analysis_by_expense(
    expense_id: UUID,
    db: Session = Depends(get_db),
):

    return ai_analysis_service.get_by_expense(
        db,
        expense_id,
    )