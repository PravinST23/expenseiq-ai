"""
Duplicate Check Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class DuplicateCheck(BaseModel):
    """
    Stores duplicate expense detection result.
    """

    __tablename__ = "duplicate_checks"

    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expenses.id"),
        unique=True,
        nullable=False,
    )

    duplicate_found: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    confidence_score: Mapped[Decimal] = mapped_column(
        Numeric(5, 2),
        default=0,
        nullable=False,
    )

    matched_expense_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("expenses.id"),
        nullable=True,
    )

    match_fields: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="duplicate_check",
        foreign_keys=[expense_id],
    )