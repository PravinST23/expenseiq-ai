"""
Employee Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field

EmployeeRole = Literal[
    "EMPLOYEE",
    "HR_HEAD",
    "CFO",
]


class EmployeeBase(BaseModel):
    """
    Common Employee Fields.
    """

    employee_code: str = Field(
        ...,
        description="Unique Employee Code",
        examples=["EMP001"],
    )

    full_name: str = Field(
        ...,
        description="Employee Full Name",
        examples=["John"],
    )

    email: EmailStr = Field(
        ...,
        description="Official Email Address",
        examples=["pravin@example.com"],
    )

    phone_number: str | None = Field(
        default=None,
        description="Employee Contact Number",
        examples=["9876543210"],
    )

    department: str = Field(
        ...,
        description="Department Name",
        examples=["Engineering"],
    )

    designation: str = Field(
        ...,
        description="Employee Designation",
        examples=["Software Engineer"],
    )

    team_id: UUID | None = Field(
        default=None,
        description="Which MAC team this employee belongs to.",
    )

    manager_id: UUID | None = Field(
        default=None,
        description=(
            "Reporting Manager (RM) - drives approval routing. "
            "Null only for the CFO/HR Head at the top of the chain."
        ),
    )


class EmployeeCreate(EmployeeBase):
    """
    Request schema for creating an Employee. Gated to HR_HEAD - see
    POST /auth/signup for the public self-service path, which forces
    role=EMPLOYEE and cannot set it.
    """

    role: EmployeeRole = Field(
        default="EMPLOYEE",
        description=(
            "HR_HEAD and CFO are the two department-head roles that "
            "terminate every approval chain - see "
            "app.workflow.manager_chain."
        ),
    )

    password: str | None = Field(
        default=None,
        min_length=6,
        description=(
            "Optional - only employees created with a password can "
            "log in via /api/v1/auth/login."
        ),
    )


class EmployeeUpdate(BaseModel):
    """
    Request schema for updating an Employee.
    """

    employee_code: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    department: str | None = None
    designation: str | None = None
    team_id: UUID | None = None
    manager_id: UUID | None = None
    employee_status: str | None = None
    is_active: bool | None = None
    policy_tier: str | None = None
    role: EmployeeRole | None = None
    password: str | None = Field(default=None, min_length=6)


class EmployeeResponse(EmployeeBase):
    """
    Response schema. hashed_password is intentionally never
    included here.
    """

    id: UUID
    employee_status: str
    is_active: bool
    policy_tier: str
    role: str
    has_password: bool = Field(
        description="Whether this employee can log in.",
    )
    manager_name: str | None = Field(
        default=None,
        description="Denormalized from manager_id for display.",
    )
    team_name: str | None = Field(
        default=None,
        description="Denormalized from team_id for display.",
    )

    model_config = ConfigDict(
        from_attributes=True
    )
