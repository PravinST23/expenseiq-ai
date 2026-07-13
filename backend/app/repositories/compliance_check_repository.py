"""
Compliance Check Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.compliance_check import ComplianceCheck
from app.repositories.base_repository import BaseRepository


class ComplianceCheckRepository(BaseRepository[ComplianceCheck]):
    """
    Repository for Compliance Check operations.
    """

    def __init__(self):
        super().__init__(ComplianceCheck)

    def get_by_expense_id(
        self,
        db: Session,
        expense_id,
    ):
        return (
            db.query(ComplianceCheck)
            .filter(ComplianceCheck.expense_id == expense_id)
            .first()
        )


compliance_check_repository = ComplianceCheckRepository()