"""
Expense AI Analysis Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.ai_review import AIAnalysis
from app.repositories.base_repository import BaseRepository


class AIAnalysisRepository(
    BaseRepository[AIAnalysis]
):
    """
    Repository for AI Analysis operations.
    """

    def __init__(self):
        super().__init__(AIAnalysis)

    def get_by_id(
        self,
        db: Session,
        analysis_id: UUID,
    ):
        """
        Get AI Analysis by ID.
        """

        return (
            db.query(AIAnalysis)
            .filter(
                AIAnalysis.id == analysis_id
            )
            .first()
        )

    def get_by_expense(
        self,
        db: Session,
        expense_id: UUID,
    ):
        """
        Get AI Analysis by Expense ID.
        """

        return (
            db.query(AIAnalysis)
            .filter(
                AIAnalysis.expense_id == expense_id
            )
            .all()
        )

    def get_by_receipt(
        self,
        db: Session,
        receipt_id: UUID,
    ):
        """
        Get AI Analysis by Receipt ID.
        """

        return (
            db.query(AIAnalysis)
            .filter(
                AIAnalysis.receipt_id == receipt_id
            )
            .first()
        )

    def update(
        self,
        db: Session,
        analysis: AIAnalysis,
    ):
        """
        Update AI Analysis.
        """

        db.commit()

        db.refresh(
            analysis,
        )

        return analysis

    def delete(
        self,
        db: Session,
        analysis: AIAnalysis,
    ):
        """
        Delete AI Analysis.
        """

        db.delete(
            analysis,
        )

        db.commit()


ai_analysis_repository = AIAnalysisRepository()