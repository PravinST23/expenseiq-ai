"""
Employee Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import employee_repository
from app.schemas.employee import EmployeeCreate
from app.schemas.employee import EmployeeUpdate


class EmployeeService:

    def create_employee(
        self,
        db: Session,
        employee: EmployeeCreate,
    ):

        existing = employee_repository.get_by_employee_code(
            db,
            employee.employee_code,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Employee Code already exists.",
            )

        existing_email = employee_repository.get_by_email(
            db,
            employee.email,
        )

        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already exists.",
            )

        new_employee = Employee(
            **employee.model_dump()
        )

        return employee_repository.create(
            db,
            new_employee,
        )

    def get_all(
        self,
        db: Session,
    ):
        return employee_repository.get_all(db)

    def get_by_id(
        self,
        db: Session,
        employee_id: UUID,
    ):

        employee = employee_repository.get_by_id(
            db,
            employee_id,
        )

        if employee is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Employee not found.",
            )

        return employee

    def update_employee(
        self,
        db: Session,
        employee_id: UUID,
        employee_update: EmployeeUpdate,
    ):

        employee = self.get_by_id(
            db,
            employee_id,
        )

        update_data = employee_update.model_dump(
            exclude_unset=True
        )

        for key, value in update_data.items():
            setattr(
                employee,
                key,
                value,
            )

        return employee_repository.update(
            db,
            employee,
        )

    def delete_employee(
        self,
        db: Session,
        employee_id: UUID,
    ):

        employee = self.get_by_id(
            db,
            employee_id,
        )

        employee_repository.delete(
            db,
            employee,
        )


employee_service = EmployeeService()