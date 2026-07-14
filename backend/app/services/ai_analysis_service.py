"""
Expense AI Analysis Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.ai_review import AIAnalysis
from app.repositories.ai_analysis_repository import (
    ai_analysis_repository,
)
from app.schemas.ai_analysis import AIAnalysisCreate
from app.schemas.ai_analysis import AIAnalysisUpdate


class AIAnalysisService:
    """
    Business logic for AI Analysis.
    """

    def create_analysis(
        self,
        db: Session,
        analysis: AIAnalysisCreate,
    ):
        """
        Create AI Analysis.
        """

        existing = (
            ai_analysis_repository.get_by_receipt(
                db,
                analysis.receipt_id,
            )
        )

        if existing:

            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    "AI Analysis already exists "
                    "for this receipt."
                ),
            )

        new_analysis = AIAnalysis(
            **analysis.model_dump()
        )

        return ai_analysis_repository.create(
            db,
            new_analysis,
        )

    def get_all(
        self,
        db: Session,
    ):
        """
        Get all AI Analyses.
        """

        return ai_analysis_repository.get_all(
            db,
        )

    def get_by_id(
        self,
        db: Session,
        analysis_id: UUID,
    ):
        """
        Get AI Analysis by ID.
        """

        analysis = (
            ai_analysis_repository.get_by_id(
                db,
                analysis_id,
            )
        )

        if analysis is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI Analysis not found.",
            )

        return analysis

    def get_by_expense(
        self,
        db: Session,
        expense_id: UUID,
    ):
        """
        Get AI Analysis by Expense.
        """

        return (
            ai_analysis_repository.get_by_expense(
                db,
                expense_id,
            )
        )

    def get_by_receipt(
        self,
        db: Session,
        receipt_id: UUID,
    ):
        """
        Get AI Analysis by Receipt.
        """

        analysis = (
            ai_analysis_repository.get_by_receipt(
                db,
                receipt_id,
            )
        )

        if analysis is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="AI Analysis not found.",
            )

        return analysis

    def update_analysis(
        self,
        db: Session,
        analysis_id: UUID,
        analysis_update: AIAnalysisUpdate,
    ):
        """
        Update AI Analysis.
        """

        analysis = self.get_by_id(
            db,
            analysis_id,
        )

        update_data = (
            analysis_update.model_dump(
                exclude_unset=True,
            )
        )

        for key, value in update_data.items():

            setattr(
                analysis,
                key,
                value,
            )

        return ai_analysis_repository.update(
            db,
            analysis,
        )

    def delete_analysis(
        self,
        db: Session,
        analysis_id: UUID,
    ):
        """
        Delete AI Analysis.
        """

        analysis = self.get_by_id(
            db,
            analysis_id,
        )

        ai_analysis_repository.delete(
            db,
            analysis,
        )


ai_analysis_service = AIAnalysisService()