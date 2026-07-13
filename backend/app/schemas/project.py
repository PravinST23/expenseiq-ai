"""
Project Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ProjectBase(BaseModel):
    """
    Common Project fields.
    """

    project_code: str
    project_name: str
    client_name: str
    project_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    project_manager: str | None = None
    project_budget: Decimal | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):

    project_name: str | None = None
    client_name: str | None = None
    project_description: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    project_manager: str | None = None
    project_budget: Decimal | None = None
    project_status: str | None = None
    is_active: bool | None = None


class ProjectResponse(ProjectBase):

    id: UUID
    project_status: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )