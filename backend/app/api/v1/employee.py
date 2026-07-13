"""
Employee API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeResponse
from app.services.employee_service import employee_service

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    summary="Create Employee",
)
def create_employee(
    employee: EmployeeCreate,
    db: Session = Depends(get_db),
):

    return employee_service.create_employee(
        db,
        employee,
    )


@router.get(
    "/",
    response_model=list[EmployeeResponse],
    summary="Get Employees",
)
def get_employees(
    db: Session = Depends(get_db),
):

    return employee_service.get_all(db)