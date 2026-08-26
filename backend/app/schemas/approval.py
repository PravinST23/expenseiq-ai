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

    # approver_role/approver_name/approval_level are only actually
    # used verbatim when the caller drives ApprovalService directly
    # (see scripts/seed_demo_data.py). Over the authenticated HTTP
    # API, they're overridden server-side from the JWT's identity -
    # see ApprovalService.create_approval - so a caller can never
    # forge an approval as a role/person they aren't. Optional here
    # so the (now-required-to-be-authenticated) frontend doesn't
    # need to send placeholder values.
    approver_role: str = "EMPLOYEE"
    approval_level: int = 1
    approver_name: str = "Unknown"

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