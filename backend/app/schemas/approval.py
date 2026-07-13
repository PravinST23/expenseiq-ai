"""
Expense Approval Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ApprovalBase(BaseModel):
    """
    Common Approval fields.
    """

    expense_id: UUID
    approver_role: str
    approver_name: str
    action: str
    comments: str | None = None


class ApprovalCreate(ApprovalBase):
    """
    Request schema for creating an approval.
    """
    pass


class ApprovalUpdate(BaseModel):
    """
    Request schema for updating an approval.
    """

    action: str | None = None
    comments: str | None = None


class ApprovalResponse(ApprovalBase):
    """
    Response schema.
    """

    id: UUID
    approved_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )