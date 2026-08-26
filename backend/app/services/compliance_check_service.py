"""
Compliance Check Service
"""

from sqlalchemy.orm import Session

from app.models.compliance_check import ComplianceCheck
from app.repositories.compliance_check_repository import (
    compliance_check_repository,
)
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

    def upsert(
        self,
        db: Session,
        expense_id,
        policy_status: str,
        policy_reason: str | None,
        ai_model: str,
    ) -> ComplianceCheck:
        """
        Create or update the compliance check result for an
        expense - called by the AI pipeline after every Groq
        policy validation.
        """

        existing = compliance_check_repository.get_by_expense_id(
            db,
            expense_id,
        )

        if existing:

            existing.policy_status = policy_status
            existing.policy_reason = policy_reason
            existing.ai_model = ai_model

            return compliance_check_repository.update(
                db,
                existing,
            )

        new_record = ComplianceCheck(
            expense_id=expense_id,
            policy_status=policy_status,
            policy_reason=policy_reason,
            ai_model=ai_model,
        )

        return compliance_check_repository.create(
            db,
            new_record,
        )

    def get_all(self, db: Session):
        return compliance_check_repository.get_all(db)

    def get_by_expense(self, db: Session, expense_id):
        return compliance_check_repository.get_by_expense_id(
            db,
            expense_id,
        )


compliance_check_service = ComplianceCheckService()
