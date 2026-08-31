"""
Team (MAC) Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class TeamBase(BaseModel):

    team_code: str = Field(..., examples=["MAC3"])
    team_name: str = Field(..., examples=["Polaris"])


class TeamCreate(TeamBase):
    pass


class TeamUpdate(BaseModel):

    team_code: str | None = None
    team_name: str | None = None
    is_active: bool | None = None


class TeamResponse(TeamBase):

    id: UUID
    is_active: bool
    employee_count: int = Field(
        description="Live count of employees currently on this team.",
    )

    model_config = ConfigDict(from_attributes=True)
