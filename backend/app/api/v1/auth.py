"""
Auth API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter
from fastapi import Depends
from fastapi import status
from sqlalchemy.orm import Session

from app.api.deps import get_current_employee
from app.api.deps import get_db
from app.models.employee import Employee
from app.schemas.auth import CurrentEmployeeResponse
from app.schemas.auth import LoginRequest
from app.schemas.auth import SignupRequest
from app.schemas.auth import TokenResponse
from app.services.auth_service import auth_service

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Sign Up",
    description=(
        "Public self-service registration - always creates an "
        "EMPLOYEE-role account and logs you straight in. Pick your "
        "MAC team and your Reporting Manager from the employee "
        "list."
    ),
)
def signup(
    signup_request: SignupRequest,
    db: Session = Depends(get_db),
):

    return auth_service.signup(db, signup_request)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login",
    description=(
        "Exchange an employee's email + password for a JWT access "
        "token. Only employees created with a password (see "
        "POST /employees/) can log in."
    ),
)
def login(
    credentials: LoginRequest,
    db: Session = Depends(get_db),
):

    return auth_service.login(db, credentials)


@router.get(
    "/me",
    response_model=CurrentEmployeeResponse,
    summary="Current Authenticated Employee",
    description=(
        "Protected - resolves the bearer token back to the "
        "authenticated employee. Useful for verifying a token is "
        "still valid client-side."
    ),
)
def read_current_employee(
    current_employee: Employee = Depends(get_current_employee),
):

    return current_employee
