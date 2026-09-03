"""
Expense Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.ai_review import AIAnalysis
from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.project import Project
    from app.models.receipt import Receipt
    from app.models.approval import ExpenseApproval
    from app.models.duplicate_check import DuplicateCheck
    from app.models.compliance_check import ComplianceCheck


class Expense(BaseModel):
    """
    Expense Transaction Table.
    """

    __tablename__ = "expenses"

    expense_number: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    employee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("employees.id"),
        nullable=False,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
    )

    expense_category: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    merchant_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
    )

    payment_method: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Pending",
        nullable=False,
    )

    # ---------------------------------------------------------
    # Hybrid Router
    # ---------------------------------------------------------

    is_sensitive: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    processing_engine: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # ---------------------------------------------------------
    # AI Risk Scoring (denormalized from latest AIAnalysis
    # for fast dashboard / Power BI querying)
    # ---------------------------------------------------------

    fraud_risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    compliance_risk_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    ai_confidence_score: Mapped[Decimal | None] = mapped_column(
        Numeric(5, 2),
        nullable=True,
    )

    is_duplicate: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    ai_recommendation: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    # ---------------------------------------------------------
    # Approval Routing (L1 Manager / L2 Finance / L3 CFO)
    # ---------------------------------------------------------

    current_approval_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    required_approval_level: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Reimbursement Tracking
    # ---------------------------------------------------------

    reimbursement_state: Mapped[str] = mapped_column(
        String(20),
        default="PENDING",
        nullable=False,
    )

    reimbursement_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    reimbursement_processed_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_reviews: Mapped[list["AIAnalysis"]] = relationship(
        "AIAnalysis",
        back_populates="expense",
        cascade="all, delete-orphan",
    )

    # ---------------------------------------------------------
    # Relationships
    # ---------------------------------------------------------

    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="expenses",
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="expenses",
    )

    receipts: Mapped[list["Receipt"]] = relationship(
        "Receipt",
        back_populates="expense",
        cascade="all, delete-orphan",
    )

    approvals: Mapped[list["ExpenseApproval"]] = relationship(
        "ExpenseApproval",
        back_populates="expense",
        cascade="all, delete-orphan",
    )

    duplicate_check: Mapped["DuplicateCheck"] = relationship(
        "DuplicateCheck",
        back_populates="expense",
        uselist=False,
        foreign_keys="DuplicateCheck.expense_id",
        cascade="all, delete-orphan",
    )

    compliance_check: Mapped["ComplianceCheck"] = relationship(
        "ComplianceCheck",
        back_populates="expense",
        uselist=False,
        cascade="all, delete-orphan",
    )

    