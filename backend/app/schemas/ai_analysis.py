"""
Expense AI Analysis Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import date
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class AIAnalysisBase(BaseModel):
    """
    Common AI Analysis fields.
    """

    expense_id: UUID

    receipt_id: UUID

    merchant_name: str | None = None

    expense_date: date | None = None

    expense_category: str | None = None

    total_amount: float | None = None

    currency: str | None = None

    payment_method: str | None = None

    ocr_text: str | None = None

    extracted_json: str | None = None

    policy_status: str

    policy_reason: str | None = None

    requires_manager_approval: bool

    approval_recommendation: str

    ai_provider: str = "Gemini"

    ocr_provider: str = "Tesseract"

    policy_provider: str = "Groq"

    pipeline_version: str = "1.0.0"

    confidence_score: float | None = None

    fraud_score: float | None = None

    duplicate_score: float | None = None

    quality_score: float | None = None


class AIAnalysisCreate(AIAnalysisBase):
    """
    Create AI Analysis.
    """
    pass


class AIAnalysisUpdate(BaseModel):
    """
    Update AI Analysis.
    """

    merchant_name: str | None = None

    expense_date: date | None = None

    expense_category: str | None = None

    total_amount: float | None = None

    currency: str | None = None

    payment_method: str | None = None

    ocr_text: str | None = None

    extracted_json: str | None = None

    policy_status: str | None = None

    policy_reason: str | None = None

    requires_manager_approval: bool | None = None

    approval_recommendation: str | None = None

    confidence_score: float | None = None

    fraud_score: float | None = None

    duplicate_score: float | None = None

    quality_score: float | None = None


class AIAnalysisResponse(AIAnalysisBase):
    """
    AI Analysis Response.
    """

    id: UUID

    processed_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )