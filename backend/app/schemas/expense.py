"""
Expense Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import date
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ExpenseBase(BaseModel):
    """
    Common Expense Fields.
    """

    expense_number: str = Field(..., examples=["EXP001"])
    # Optional over the authenticated HTTP API - the server always
    # submits the expense as the logged-in employee (see
    # ExpenseService.create_expense), overriding whatever is sent
    # here. Only trusted internal callers without a token (import
    # scripts) need to set it explicitly.
    employee_id: UUID | None = None
    project_id: UUID
    expense_category: str
    merchant_name: str
    amount: Decimal
    currency: str = "INR"
    expense_date: date
    payment_method: str
    description: str | None = None
    is_sensitive: bool = False


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):

    expense_number: str | None = None
    employee_id: UUID | None = None
    project_id: UUID | None = None
    expense_category: str | None = None
    merchant_name: str | None = None
    amount: Decimal | None = None
    currency: str | None = None
    expense_date: date | None = None
    payment_method: str | None = None
    description: str | None = None
    status: str | None = None
    is_sensitive: bool | None = None


class ReimbursementUpdate(BaseModel):
    """
    Request schema for advancing reimbursement state.
    """

    reimbursement_state: str = Field(
        ...,
        description="One of PENDING, APPROVED, PAID",
        examples=["PAID"],
    )
    # Optional over the authenticated HTTP API - overridden
    # server-side from the JWT identity when present (see
    # ExpenseService.update_reimbursement). Required only for
    # trusted internal callers that bypass auth (seed scripts).
    processed_by: str | None = None


class ExpenseResponse(ExpenseBase):

    id: UUID
    status: str

    processing_engine: str | None = None

    fraud_risk_score: Decimal | None = None
    compliance_risk_score: Decimal | None = None
    ai_confidence_score: Decimal | None = None
    is_duplicate: bool
    ai_recommendation: str | None = None

    current_approval_level: int
    required_approval_level: int

    reimbursement_state: str
    reimbursement_updated_at: datetime | None = None
    reimbursement_processed_by: str | None = None

    model_config = ConfigDict(
        from_attributes=True
    )