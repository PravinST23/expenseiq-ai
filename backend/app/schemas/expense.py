"""
Expense Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import date
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
    employee_id: UUID
    project_id: UUID
    expense_category: str
    merchant_name: str
    amount: Decimal
    currency: str = "INR"
    expense_date: date
    payment_method: str
    description: str | None = None


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


class ExpenseResponse(ExpenseBase):

    id: UUID
    status: str

    model_config = ConfigDict(
        from_attributes=True
    )