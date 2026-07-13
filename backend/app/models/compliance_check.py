"""
Compliance Check Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class ComplianceCheck(BaseModel):
    """
    Stores AI policy validation result.
    """

    __tablename__ = "compliance_checks"

    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expenses.id"),
        unique=True,
        nullable=False,
    )

    policy_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    policy_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ai_model: Mapped[str] = mapped_column(
        String(50),
        default="Gemini",
        nullable=False,
    )

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="compliance_check",
    )