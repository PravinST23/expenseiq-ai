"""
Employee Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.employee import Employee
from app.repositories.base_repository import BaseRepository


class EmployeeRepository(BaseRepository[Employee]):
    """
    Repository for Employee operations.
    """

    def __init__(self):
        super().__init__(Employee)

    def get_by_employee_code(
        self,
        db: Session,
        employee_code: str,
    ):
        return (
            db.query(Employee)
            .filter(Employee.employee_code == employee_code)
            .first()
        )

    def get_by_email(
        self,
        db: Session,
        email: str,
    ):
        return (
            db.query(Employee)
            .filter(Employee.email == email)
            .first()
        )

    def get_by_id(
        self,
        db: Session,
        employee_id: UUID,
    ):
        return (
            db.query(Employee)
            .filter(Employee.id == employee_id)
            .first()
        )

    def update(
        self,
        db: Session,
        employee: Employee,
    ):
        db.commit()
        db.refresh(employee)
        return employee

    def delete(
        self,
        db: Session,
        employee: Employee,
    ):
        db.delete(employee)
        db.commit()


employee_repository = EmployeeRepository()