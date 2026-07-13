"""
Employee Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr


class EmployeeBase(BaseModel):
    """
    Common Employee fields.
    """

    employee_code: str
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    department: str
    designation: str
    manager_name: str | None = None


class EmployeeCreate(EmployeeBase):
    """
    Request schema for creating an employee.
    """
    pass


class EmployeeUpdate(BaseModel):
    """
    Request schema for updating an employee.
    """

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