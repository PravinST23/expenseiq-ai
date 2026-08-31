"""
Team (MAC) Entity

Author: Pravin Shanmugavel
Project: ExpenseIQ

A MAC (e.g. "MAC3 - Polaris") is Psiog's internal delivery-team
grouping. Employees belong to a MAC; each MAC runs one or more
client Projects (e.g. GTF, Revlon, Stallion under MAC3).
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
    from app.models.employee import Employee
    from app.models.project import Project


class Team(BaseModel):
    """
    MAC Team Master Table.
    """

    __tablename__ = "teams"

    team_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    team_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    employees: Mapped[list["Employee"]] = relationship(
        "Employee",
        back_populates="team",
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="team",
    )

    @property
    def employee_count(self) -> int:
        """
        Live headcount - computed, not stored, so it can never drift
        from the actual employees table.
        """
        return len(self.employees)
