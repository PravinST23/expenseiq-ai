"""
Receipt Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class Receipt(BaseModel):
    """
    Receipt Master Table.
    """

    __tablename__ = "receipts"

    receipt_number: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        index=True,
        nullable=False,
    )

    expense_id: Mapped[str] = mapped_column(
        ForeignKey("expenses.id"),
        nullable=False,
    )

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    upload_status: Mapped[str] = mapped_column(
        String(30),
        default="Uploaded",
        nullable=False,
    )

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="receipts",
    )