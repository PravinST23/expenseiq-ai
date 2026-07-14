"""
Receipt Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from app.models.ai_review import AIAnalysis
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

    ai_reviews: Mapped[list["AIAnalysis"]] = relationship(
        "AIAnalysis",
        back_populates="receipt",
    )

    # ---------------------------------------------------------
    # OCR Fields
    # ---------------------------------------------------------

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    ocr_status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
        nullable=False,
    )

    ocr_processed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # ---------------------------------------------------------
    # AI Fields (Future - Gemini)
    # ---------------------------------------------------------

    ai_status: Mapped[str] = mapped_column(
        String(20),
        default="Pending",
        nullable=False,
    )

    extracted_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # ---------------------------------------------------------
    # Relationship
    # ---------------------------------------------------------

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="receipts",
    )