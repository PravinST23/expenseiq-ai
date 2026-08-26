"""
Duplicate Check Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class DuplicateCheckBase(BaseModel):

    expense_id: UUID
    duplicate_found: bool
    confidence_score: Decimal
    matched_expense_id: UUID | None = None
    match_fields: str | None = None


class DuplicateCheckCreate(DuplicateCheckBase):
    pass


class DuplicateCheckResponse(DuplicateCheckBase):

    id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )