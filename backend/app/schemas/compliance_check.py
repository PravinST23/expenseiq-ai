"""
Compliance Check Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ComplianceCheckBase(BaseModel):

    expense_id: UUID
    policy_status: str
    policy_reason: str | None = None
    ai_model: str = "Gemini"


class ComplianceCheckCreate(ComplianceCheckBase):
    pass


class ComplianceCheckResponse(ComplianceCheckBase):

    id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )