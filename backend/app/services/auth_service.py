"""
Auth Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.security import verify_password
from app.models.employee import Employee
from app.repositories.employee_repository import employee_repository
from app.schemas.auth import LoginRequest
from app.schemas.auth import TokenResponse

INVALID_CREDENTIALS_DETAIL = "Incorrect email or password."


class AuthService:

    def authenticate(
        self,
        db: Session,
        credentials: LoginRequest,
    ) -> Employee:
        """
        Verify an email/password pair. Raises 401 for any failure
        mode (unknown email, no password set, wrong password,
        inactive account) without distinguishing which - avoids
        leaking which emails are registered.
        """

        employee = employee_repository.get_by_email(
            db,
            credentials.email,
        )

        if employee is None or employee.hashed_password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS_DETAIL,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not verify_password(
            credentials.password,
            employee.hashed_password,
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=INVALID_CREDENTIALS_DETAIL,
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not employee.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This employee account is inactive.",
            )

        return employee

    def login(
        self,
        db: Session,
        credentials: LoginRequest,
    ) -> TokenResponse:

        employee = self.authenticate(db, credentials)

        token, expires_at = create_access_token(
            employee_id=employee.id,
            role=employee.role,
        )

        return TokenResponse(
            access_token=token,
            expires_at=expires_at,
            employee_id=employee.id,
            employee_code=employee.employee_code,
            full_name=employee.full_name,
            role=employee.role,
        )


auth_service = AuthService()
