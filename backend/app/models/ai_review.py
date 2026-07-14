"""
Expense AI Analysis Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from datetime import date
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import func
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.receipt import Receipt


class AIAnalysis(BaseModel):
    """
    Stores AI generated analysis for an expense receipt.
    """

    __tablename__ = "expense_ai_analysis"

    # =====================================================
    # Relationships
    # =====================================================

    expense_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("expenses.id"),
        nullable=False,
    )

    receipt_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("receipts.id"),
        nullable=False,
    )

    # =====================================================
    # Receipt Information
    # =====================================================

    merchant_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    expense_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    expense_category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    total_amount: Mapped[float | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    currency: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    payment_method: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    # =====================================================
    # OCR & AI
    # =====================================================

    ocr_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extracted_json: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # =====================================================
    # Policy Validation
    # =====================================================

    policy_status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    policy_reason: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    requires_manager_approval: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    approval_recommendation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    # =====================================================
    # AI Metadata
    # =====================================================

    ai_provider: Mapped[str] = mapped_column(
        String(50),
        default="Gemini",
        nullable=False,
    )

    ocr_provider: Mapped[str] = mapped_column(
        String(50),
        default="Tesseract",
        nullable=False,
    )

    policy_provider: Mapped[str] = mapped_column(
        String(50),
        default="Groq",
        nullable=False,
    )

    pipeline_version: Mapped[str] = mapped_column(
        String(20),
        default="1.0.0",
        nullable=False,
    )

    # =====================================================
    # Future AI Enhancements
    # =====================================================

    confidence_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    fraud_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    duplicate_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    quality_score: Mapped[float | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    # =====================================================
    # Audit
    # =====================================================

    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # =====================================================
    # Relationships
    # =====================================================

    expense: Mapped["Expense"] = relationship(
        "Expense",
        back_populates="ai_reviews",
    )

    receipt: Mapped["Receipt"] = relationship(
        "Receipt",
        back_populates="ai_reviews",
    )