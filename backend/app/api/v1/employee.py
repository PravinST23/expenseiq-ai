"""
Employee API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import Response
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeResponse
from app.schemas.employee import EmployeeUpdate
from app.services.employee_service import employee_service

router = APIRouter(
    prefix="/employees",
    tags=["Employees"],
)


@router.post(
    "/",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
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


@router.get(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Get Employee By ID",
)
def get_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
):

    return employee_service.get_by_id(
        db,
        employee_id,
    )


@router.put(
    "/{employee_id}",
    response_model=EmployeeResponse,
    summary="Update Employee",
)
def update_employee(
    employee_id: UUID,
    employee: EmployeeUpdate,
    db: Session = Depends(get_db),
):

    return employee_service.update_employee(
        db,
        employee_id,
        employee,
    )


@router.delete(
    "/{employee_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Employee",
)
def delete_employee(
    employee_id: UUID,
    db: Session = Depends(get_db),
):

    employee_service.delete_employee(
        db,
        employee_id,
    )

    return Response(status_code=status.HTTP_204_NO_CONTENT)