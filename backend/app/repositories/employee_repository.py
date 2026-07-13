"""
Employee Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

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


employee_repository = EmployeeRepository()