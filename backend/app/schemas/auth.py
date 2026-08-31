"""
Auth Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import EmailStr
from pydantic import Field


class LoginRequest(BaseModel):
    """
    Request schema for POST /auth/login.
    """

    email: EmailStr
    password: str


class SignupRequest(BaseModel):
    """
    Request schema for POST /auth/signup - the public self-service
    registration path. Always creates an EMPLOYEE-role account
    (there is no way to request HR_HEAD/CFO here); employee_code is
    generated server-side.
    """

    full_name: str = Field(..., examples=["Ananya Sharma"])
    email: EmailStr
    password: str = Field(..., min_length=6)
    phone_number: str | None = None
    department: str
    designation: str
    team_id: UUID = Field(
        ...,
        description="Which MAC team this employee belongs to.",
    )
    manager_id: UUID | None = Field(
        default=None,
        description="Reporting Manager - pick your RM from the employee list.",
    )


class TokenResponse(BaseModel):
    """
    Response schema for a successful login.
    """

    access_token: str
    token_type: str = "bearer"
    expires_at: datetime

    employee_id: UUID
    employee_code: str
    full_name: str
    role: str


class CurrentEmployeeResponse(BaseModel):
    """
    Response schema for GET /auth/me - proves token validation
    actually resolves back to the authenticated identity.
    """

    id: UUID
    employee_code: str
    full_name: str
    email: EmailStr
    role: str

    model_config = ConfigDict(from_attributes=True)
