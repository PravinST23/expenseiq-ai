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
from pydantic import Field


class ProjectBase(BaseModel):
    """
    Common Project Fields.
    """

    project_code: str = Field(
        ...,
        examples=["PRJ001"],
    )

    project_name: str = Field(
        ...,
        examples=["ExpenseIQ"],
    )

    client_name: str = Field(
        ...,
        examples=["Internal"],
    )

    project_description: str | None = None

    start_date: date | None = None

    end_date: date | None = None

    project_manager: str | None = None

    project_budget: Decimal | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):

    project_code: str | None = None
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