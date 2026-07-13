"""
Project Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import Date
from sqlalchemy import Numeric
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class Project(BaseModel):
    """
    Project Master Table.
    """

    __tablename__ = "projects"

    project_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    project_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    client_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    project_description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    start_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    end_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    project_manager: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    project_budget: Mapped[Decimal | None] = mapped_column(
        Numeric(12, 2),
        nullable=True,
    )

    project_status: Mapped[str] = mapped_column(
        String(30),
        default="Active",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="project",
    )