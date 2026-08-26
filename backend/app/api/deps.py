"""
Shared API Dependencies

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from collections.abc import Generator
from uuid import UUID

from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import InvalidTokenError
from app.core.security import decode_access_token
from app.database.session import SessionLocal
from app.models.employee import Employee
from app.repositories.employee_repository import employee_repository


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# tokenUrl is only used to populate Swagger's "Authorize" dialog -
# this API takes JSON login credentials, not an OAuth2 form.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/v1/auth/login",
    auto_error=False,
)

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_employee(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Employee:
    """
    Resolve the JWT bearer token on the request into the
    authenticated Employee. Raises 401 for a missing, malformed,
    forged, or expired token, or one referring to a deleted
    employee.
    """

    if token is None:
        raise CREDENTIALS_EXCEPTION

    try:
        payload = decode_access_token(token)
    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    try:
        employee_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise CREDENTIALS_EXCEPTION

    employee = employee_repository.get_by_id(db, employee_id)

    if employee is None or not employee.is_active:
        raise CREDENTIALS_EXCEPTION

    return employee


def require_roles(*allowed_roles: str):
    """
    Dependency factory - gates a route to specific employee roles
    on top of get_current_employee's authentication check.

    Usage: Depends(require_roles("L2_FINANCE", "L3_CFO"))
    """

    def _check(
        current_employee: Employee = Depends(get_current_employee),
    ) -> Employee:

        if current_employee.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Role '{current_employee.role}' is not "
                    f"permitted to perform this action. Requires "
                    f"one of: {', '.join(allowed_roles)}."
                ),
            )

        return current_employee

    return _check
