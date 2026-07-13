"""
Employee Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.employee_repository import employee_repository
from app.schemas.employee import EmployeeCreate


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
            raise ValueError(
                "Employee Code already exists."
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
        employee_id,
    ):
        return employee_repository.get_by_id(
            db,
            employee_id,
        )


employee_service = EmployeeService()