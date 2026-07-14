"""
Receipt Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json
from datetime import datetime
from sqlalchemy.orm import Session
from uuid import UUID

from fastapi import HTTPException
from fastapi import status

from app.langchain.expense_pipeline import expense_pipeline
from app.models.receipt import Receipt
from app.repositories.receipt_repository import receipt_repository
from app.schemas.ai_analysis import AIAnalysisCreate
from app.schemas.receipt import ReceiptCreate
from app.schemas.receipt import ReceiptUpdate
from app.services.ai_analysis_service import ai_analysis_service


class ReceiptService:
    """
    Business logic for Receipt operations.
    """

    def create_receipt(
        self,
        db: Session,
        receipt: ReceiptCreate,
    ):
        """
        Create a new receipt.
        """

        existing = receipt_repository.get_by_receipt_number(
            db,
            receipt.receipt_number,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Receipt Number already exists.",
            )

        new_receipt = Receipt(
            **receipt.model_dump()
        )

        return receipt_repository.create(
            db,
            new_receipt,
        )

    def upload_receipt(
        self,
        db: Session,
        receipt: ReceiptCreate,
    ):
        """
        Upload receipt and process using AI Pipeline.
        """

        # -------------------------------------------------
        # Save Receipt
        # -------------------------------------------------

        new_receipt = self.create_receipt(
            db,
            receipt,
        )

        try:

            # -------------------------------------------------
            # AI Pipeline
            # -------------------------------------------------

            result = expense_pipeline.process_receipt(
                new_receipt.file_path,
            )

            # -------------------------------------------------
            # Update Receipt
            # -------------------------------------------------

            new_receipt.ocr_text = result.get(
                "ocr_text",
            )

            new_receipt.ocr_status = "Completed"

            new_receipt.ocr_processed_at = datetime.utcnow()

            new_receipt.extracted_json = json.dumps(
                result,
                indent=4,
            )

            new_receipt.ai_status = "Completed"

            receipt_repository.update(
                db,
                new_receipt,
            )

            # -------------------------------------------------
            # Save AI Analysis
            # -------------------------------------------------

            analysis = AIAnalysisCreate(

                expense_id=receipt.expense_id,

                receipt_id=new_receipt.id,

                merchant_name=result.get(
                    "merchant_name",
                ),

                expense_date=result.get(
                    "expense_date",
                ),

                expense_category=result.get(
                    "expense_category",
                ),

                total_amount=result.get(
                    "total_amount",
                ),

                currency=result.get(
                    "currency",
                ),

                payment_method=result.get(
                    "payment_method",
                ),

                ocr_text=result.get(
                    "ocr_text",
                ),

                extracted_json=json.dumps(
                    result,
                    indent=4,
                ),

                policy_status=result.get(
                    "policy_status",
                    "UNKNOWN",
                ),

                policy_reason=result.get(
                    "policy_reason",
                ),

                requires_manager_approval=result.get(
                    "requires_manager_approval",
                    True,
                ),

                approval_recommendation=result.get(
                    "approval_status",
                    "Pending Manager Review",
                ),

                ai_provider="Gemini",

                ocr_provider="Tesseract",

                policy_provider="Groq",

                pipeline_version="1.0.0",

                confidence_score=None,

                fraud_score=None,

                duplicate_score=None,

                quality_score=None,
            )

            ai_analysis_service.create_analysis(
                db,
                analysis,
            )

        except Exception as ex:

            print(
                f"Pipeline Error : {ex}"
            )

            new_receipt.ocr_status = "Failed"

            new_receipt.ai_status = "Failed"

            receipt_repository.update(
                db,
                new_receipt,
            )

        return new_receipt

    def get_all(
        self,
        db: Session,
    ):

        return receipt_repository.get_all(
            db,
        )

    def get_by_id(
        self,
        db: Session,
        receipt_id: UUID,
    ):

        receipt = receipt_repository.get_by_id(
            db,
            receipt_id,
        )

        if receipt is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found.",
            )

        return receipt

    def update_receipt(
        self,
        db: Session,
        receipt_id: UUID,
        receipt_update: ReceiptUpdate,
    ):

        receipt = self.get_by_id(
            db,
            receipt_id,
        )

        update_data = receipt_update.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():

            setattr(
                receipt,
                key,
                value,
            )

        return receipt_repository.update(
            db,
            receipt,
        )

    def delete_receipt(
        self,
        db: Session,
        receipt_id: UUID,
    ):

        receipt = self.get_by_id(
            db,
            receipt_id,
        )

        receipt_repository.delete(
            db,
            receipt,
        )


receipt_service = ReceiptService()