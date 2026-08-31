"""
Employee Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from app.models.base_model import BaseModel

if TYPE_CHECKING:
    from app.models.expense import Expense
    from app.models.team import Team


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
    # Org Structure
    # ---------------------------------------------------------

    # Real "reports to" link - the employee's Reporting Manager
    # (RM). Drives approval routing (see app.workflow.manager_chain)
    # instead of a free-text manager_name.
    manager_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("employees.id"),
        nullable=True,
    )

    team_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("teams.id"),
        nullable=True,
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

    # One of EMPLOYEE (default, self-service signup), HR_HEAD (final
    # approver for comp-off requests, manages employees/teams/
    # projects), CFO (final approver for expense claims and
    # reimbursement). Levels 1 & 2 of every approval chain are
    # resolved dynamically from manager_id, never from role - see
    # app.workflow.manager_chain.
    role: Mapped[str] = mapped_column(
        String(20),
        default="EMPLOYEE",
        nullable=False,
    )

    # Nullable: an Employee created without a password simply cannot
    # log in - reserved for records that predate self-service signup.
    hashed_password: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    # Relationships
    expenses: Mapped[list["Expense"]] = relationship(
        "Expense",
        back_populates="employee",
    )

    team: Mapped["Team"] = relationship(
        "Team",
        back_populates="employees",
        foreign_keys=[team_id],
    )

    manager: Mapped["Employee"] = relationship(
        "Employee",
        remote_side="Employee.id",
        foreign_keys=[manager_id],
        back_populates="direct_reports",
    )

    direct_reports: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="manager",
        foreign_keys=[manager_id],
    )

    @property
    def has_password(self) -> bool:
        """
        Whether this employee has a login-eligible password set.
        Exposed to EmployeeResponse instead of hashed_password
        itself, which must never leave the server.
        """
        return self.hashed_password is not None

    @property
    def manager_name(self) -> str | None:
        return self.manager.full_name if self.manager else None

    @property
    def team_name(self) -> str | None:
        return self.team.team_name if self.team else None
