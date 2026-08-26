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
from app.models.approval import ExpenseApproval
from app.models.expense import Expense
from app.models.receipt import Receipt
from app.repositories.receipt_repository import receipt_repository
from app.schemas.ai_analysis import AIAnalysisCreate
from app.schemas.receipt import ReceiptCreate
from app.schemas.receipt import ReceiptUpdate
from app.services.ai_analysis_service import ai_analysis_service
from app.services.compliance_check_service import (
    compliance_check_service,
)


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
        Upload receipt and process using the AI Pipeline
        (OCR -> Hybrid Router -> Duplicate Detector -> Groq
        Risk Scoring -> Auto-Approval Engine -> Approval
        Workflow).
        """

        # -------------------------------------------------
        # Save Receipt
        # -------------------------------------------------

        new_receipt = self.create_receipt(
            db,
            receipt,
        )

        expense = (
            db.query(Expense)
            .filter(Expense.id == receipt.expense_id)
            .first()
        )

        if expense is None:

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Expense not found for this receipt.",
            )

        try:

            # -------------------------------------------------
            # AI Pipeline
            # -------------------------------------------------

            result = expense_pipeline.process_receipt(
                db,
                expense,
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
                default=str,
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
                    default=str,
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
                    "ai_recommendation",
                    "ESCALATE_FOR_REVIEW",
                ),

                ai_provider=result.get(
                    "ai_provider",
                    "gemini",
                ),

                ocr_provider="Tesseract",

                policy_provider="Groq",

                pipeline_version="2.0.0",

                confidence_score=result.get(
                    "confidence",
                ),

                fraud_score=result.get(
                    "fraud_risk",
                ),

                duplicate_score=result.get(
                    "duplicate_confidence",
                ),

                quality_score=None,

                compliance_risk_score=result.get(
                    "compliance_risk",
                ),

                risk_reason=result.get(
                    "risk_reason",
                ),

                required_approval_level=result.get(
                    "required_approval_level",
                ),
            )

            ai_analysis_service.create_analysis(
                db,
                analysis,
            )

            # -------------------------------------------------
            # Upsert Compliance Check
            # -------------------------------------------------

            compliance_check_service.upsert(
                db,
                expense_id=expense.id,
                policy_status=result.get(
                    "policy_status",
                    "UNKNOWN",
                ),
                policy_reason=result.get("policy_reason"),
                ai_model=result.get("ai_provider", "gemini"),
            )

            # -------------------------------------------------
            # Update Expense (denormalized AI + routing state)
            # -------------------------------------------------

            expense.processing_engine = result.get(
                "ai_provider",
            )
            expense.fraud_risk_score = result.get(
                "fraud_risk",
            )
            expense.compliance_risk_score = result.get(
                "compliance_risk",
            )
            expense.ai_confidence_score = result.get(
                "confidence",
            )
            expense.is_duplicate = bool(
                result.get("duplicate_found", False)
            )
            expense.ai_recommendation = result.get(
                "ai_recommendation",
            )
            expense.current_approval_level = result.get(
                "current_approval_level",
                1,
            )
            expense.required_approval_level = result.get(
                "required_approval_level",
                1,
            )
            expense.status = result.get(
                "approval_status",
                "Pending L1 Manager Approval",
            )

            approved_by = result.get("approved_by")

            if approved_by == "System":

                expense.reimbursement_state = "APPROVED"
                expense.reimbursement_updated_at = (
                    datetime.utcnow()
                )
                expense.reimbursement_processed_by = "System"

                db.add(
                    ExpenseApproval(
                        expense_id=expense.id,
                        approver_role="SYSTEM",
                        approval_level=1,
                        approver_name="ExpenseIQ AI",
                        action="Approved",
                        comments=(
                            "Auto-approved by the Smart "
                            "Auto-Approval Engine: "
                            + str(
                                result.get(
                                    "auto_approval_reason",
                                    "",
                                )
                            )
                        ),
                    )
                )

            db.commit()
            db.refresh(expense)

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
