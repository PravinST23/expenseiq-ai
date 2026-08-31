"""
Expense Approval Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ApprovalCreate(BaseModel):
    """
    Request schema for creating an approval. Who is acting and at
    what level is entirely derived server-side from the
    authenticated employee + the manager-chain resolver (see
    ApprovalService.create_approval) - the caller only says what
    they did.
    """

    expense_id: UUID
    action: str
    comments: str | None = None


class ApprovalUpdate(BaseModel):
    """
    Request schema for updating an approval.
    """

    action: str | None = None
    comments: str | None = None


class ApprovalResponse(BaseModel):
    """
    Response schema.
    """

    id: UUID
    expense_id: UUID
    approver_employee_id: UUID | None = None
    approver_role: str
    approval_level: int
    approver_name: str
    action: str
    comments: str | None = None
    approved_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )
