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


class LoginRequest(BaseModel):
    """
    Request schema for POST /auth/login.
    """

    email: EmailStr
    password: str


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
