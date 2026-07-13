"""
Compliance Check Service
"""

from sqlalchemy.orm import Session

from app.models.compliance_check import ComplianceCheck
from app.repositories.compliance_check_repository import compliance_check_repository
from app.schemas.compliance_check import ComplianceCheckCreate


class ComplianceCheckService:

    def create(
        self,
        db: Session,
        compliance: ComplianceCheckCreate,
    ):

        new_record = ComplianceCheck(
            **compliance.model_dump()
        )

        return compliance_check_repository.create(
            db,
            new_record,
        )


compliance_check_service = ComplianceCheckService()