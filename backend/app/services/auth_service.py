"""
Auth Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import uuid

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.core.security import verify_password
from app.models.employee import Employee
from app.repositories.employee_repository import employee_repository
from app.schemas.auth import LoginRequest
from app.schemas.auth import SignupRequest
from app.schemas.auth import TokenResponse
from app.schemas.employee import EmployeeCreate
from app.services.employee_service import employee_service

INVALID_CREDENTIALS_DETAIL = "Incorrect email or password."


def _generate_employee_code(db: Session) -> str:
    """
    EMP + 6 hex chars, retried on the (astronomically unlikely)
    collision - public signup can't rely on a human picking a code.
    """

    for _ in range(5):

        candidate = f"EMP{uuid.uuid4().hex[:6].upper()}"

        if employee_repository.get_by_employee_code(db, candidate) is None:
            return candidate

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Could not generate a unique employee code - try again.",
    )


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

    def signup(
        self,
        db: Session,
        signup: SignupRequest,
    ) -> TokenResponse:
        """
        Public self-service registration. Always creates an
        EMPLOYEE-role account (role is never taken from the
        request) and logs the new employee straight in.
        """

        employee = employee_service.create_employee(
            db,
            EmployeeCreate(
                employee_code=_generate_employee_code(db),
                full_name=signup.full_name,
                email=signup.email,
                phone_number=signup.phone_number,
                department=signup.department,
                designation=signup.designation,
                team_id=signup.team_id,
                manager_id=signup.manager_id,
                role="EMPLOYEE",
                password=signup.password,
            ),
        )

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
