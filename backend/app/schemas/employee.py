"""
Employee Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


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

    manager_name: str | None = Field(
        default=None,
        description="Reporting Manager",
        examples=["John Smith"],
    )


class EmployeeCreate(EmployeeBase):
    """
    Request schema for creating an Employee.
    """

    pass


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
    manager_name: str | None = None
    employee_status: str | None = None
    is_active: bool | None = None


class EmployeeResponse(EmployeeBase):
    """
    Response schema.
    """

    id: UUID
    employee_status: str
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True
    )