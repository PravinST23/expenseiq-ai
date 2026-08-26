"""
Employee Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense


class Employee(BaseModel):
    """
    Employee Master Table.
    """

    __tablename__ = "employees"

    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    phone_number: Mapped[str | None] = mapped_column(
        String(15),
        nullable=True,
    )

    department: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    designation: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    manager_name: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    employee_status: Mapped[str] = mapped_column(
        String(20),
        default="Active",
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ---------------------------------------------------------
    # Policy / Risk Metadata
    # ---------------------------------------------------------

    policy_tier: Mapped[str] = mapped_column(
        String(20),
        default="STANDARD",
        nullable=False,
    )

    # ---------------------------------------------------------
    # Authentication / RBAC
    # ---------------------------------------------------------

    # One of EMPLOYEE, L1_MANAGER, L2_FINANCE, L3_CFO - see
    # app.workflow.approval_workflow.LEVEL_ROLES for the approval
    # routing roles this must line up with.
    role: Mapped[str] = mapped_column(
        String(20),
        default="EMPLOYEE",
        nullable=False,
    )

    # Nullable: an Employee created without a password (the common
    # case for most seed/demo/test records) simply cannot log in -
    # login-eligible accounts are opt-in via EmployeeCreate.password.
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="employee",
    )

    @property
    def has_password(self) -> bool:
        """
        Whether this employee has a login-eligible password set.
        Exposed to EmployeeResponse instead of hashed_password
        itself, which must never leave the server.
        """
        return self.hashed_password is not None