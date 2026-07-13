"""
Expense Approval Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class ExpenseApproval(BaseModel):
    """
    Expense Approval Audit Table.
    """

    __tablename__ = "expense_approvals"

    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expenses.id"),
        nullable=False,
    )

    approver_role: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    approver_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    action: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    comments: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    approved_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="approvals",
    )