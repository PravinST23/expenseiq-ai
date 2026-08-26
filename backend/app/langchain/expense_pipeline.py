"""
Expense Pipeline

Author: Pravin Shanmugavel
Project: ExpenseIQ

End-to-end LangChain-orchestrated receipt-to-record pipeline:

  1. Tesseract OCR                  -> raw text
  2. Hybrid Router (Gemini/Ollama)  -> structured receipt JSON
  3. LangChain Output Parser        -> validated structured record
  4. Duplicate Fraud Detector       -> duplicate_found + match info
  5. Groq Cloud Risk Scoring        -> fraud_risk / compliance_risk /
                                        confidence + policy PASS/FAIL
  6. Smart Auto-Approval Engine     -> AUTO_APPROVE / ESCALATE /
                                        REJECT recommendation +
                                        required approval level
  7. Approval Workflow              -> initial approval status
"""

from sqlalchemy.orm import Session

from app.ai.groq_service import groq_service
from app.ai.hybrid_router import hybrid_router
from app.ai.ocr_service import ocr_service
from app.langchain.output_parser import output_parser
from app.models.approval import ExpenseApproval
from app.models.expense import Expense
from app.services.duplicate_check_service import duplicate_check_service
from app.workflow.approval_workflow import approval_workflow
from app.workflow.auto_approval_engine import auto_approval_engine

REQUIRED_FIELDS_FOR_POLICY_CHECK = (
    "total_amount",
    "expense_category",
)


def _normalize_date(value):
    """
    Some receipts carry a full timestamp (e.g. a POS terminal print
    time like "2007-03-12T14:22:00") in what the AI model reports as
    expense_date. Pydantic's `date` field rejects a datetime string
    whose time isn't exactly midnight
    (`date_from_datetime_inexact`), which would otherwise fail the
    whole pipeline for an otherwise-valid receipt - so trim to the
    date component here, once, at the source.
    """

    if not isinstance(value, str):
        return value

    return value.split("T")[0].split(" ")[0] or None


class ExpensePipeline:
    """
    AI Processing Pipeline.
    """

    def process_receipt(
        self,
        db: Session,
        expense: Expense,
        image_path: str,
    ) -> dict:
        """
        Run the full receipt -> structured, risk-scored,
        routed expense record pipeline for a single receipt.
        """

        # -------------------------------------------------
        # 1. OCR
        # -------------------------------------------------

        try:

            ocr_text = ocr_service.extract_text(
                image_path,
            )

        except Exception as ex:

            print(f"OCR Error : {ex}")

            ocr_text = ""

        # -------------------------------------------------
        # 2 & 3. Hybrid Router + Structured Parsing
        # -------------------------------------------------

        try:

            ai_result = hybrid_router.route(
                image_path,
                is_sensitive=expense.is_sensitive,
            )

            engine = ai_result.pop("_engine", "gemini")
            fallback = ai_result.pop("_fallback", False)
            fallback_reason = ai_result.pop(
                "_fallback_reason",
                None,
            )

            structured_result = output_parser.parse(
                ai_result,
            )

            structured_result["expense_date"] = _normalize_date(
                structured_result.get("expense_date")
            )

            ai_success = True

        except Exception as ex:

            print(f"AI Extraction Error : {ex}")

            ai_success = False
            engine = "ollama" if expense.is_sensitive else "gemini"
            fallback = False
            fallback_reason = str(ex)

            structured_result = {
                "merchant_name": None,
                "expense_category": None,
                "expense_date": None,
                "receipt_number": None,
                "invoice_number": None,
                "gst_number": None,
                "subtotal": None,
                "tax_amount": None,
                "total_amount": None,
                "currency": None,
                "payment_method": None,
                "items": [],
            }

        # -------------------------------------------------
        # 4. Duplicate Fraud Detector
        # -------------------------------------------------

        try:

            duplicate_check = duplicate_check_service.run_check(
                db,
                expense,
            )

            duplicate_found = duplicate_check.duplicate_found
            duplicate_confidence = float(
                duplicate_check.confidence_score
            )
            duplicate_match_fields = duplicate_check.match_fields

        except Exception as ex:

            print(f"Duplicate Check Error : {ex}")

            duplicate_found = False
            duplicate_confidence = 0.0
            duplicate_match_fields = None

        # -------------------------------------------------
        # 5. Groq Policy + Risk Scoring
        # -------------------------------------------------

        has_required_fields = all(
            structured_result.get(field) is not None
            for field in REQUIRED_FIELDS_FOR_POLICY_CHECK
        )

        if ai_success and has_required_fields:

            try:

                policy_result = groq_service.validate_expense(
                    structured_result,
                )

            except Exception as ex:

                print(f"Groq Error : {ex}")

                policy_result = {
                    "status": "UNKNOWN",
                    "reason": (
                        "Policy validation could not be "
                        "completed."
                    ),
                    "requires_manager_approval": True,
                    "fraud_risk": 50,
                    "compliance_risk": 50,
                    "confidence": 0,
                }

        else:

            policy_result = {
                "status": "UNKNOWN",
                "reason": (
                    "Policy validation skipped because "
                    "receipt extraction was unsuccessful."
                ),
                "requires_manager_approval": True,
                "fraud_risk": 50,
                "compliance_risk": 50,
                "confidence": 0,
            }

        fraud_risk = float(policy_result.get("fraud_risk") or 0)
        compliance_risk = float(
            policy_result.get("compliance_risk") or 0
        )
        confidence = float(policy_result.get("confidence") or 0)

        # -------------------------------------------------
        # 6. Smart Auto-Approval Engine
        # -------------------------------------------------

        rejection_ratio = self._employee_rejection_ratio(
            db,
            expense.employee_id,
        )

        auto_approval = auto_approval_engine.evaluate(
            policy_status=policy_result["status"],
            requires_manager_approval=policy_result[
                "requires_manager_approval"
            ],
            fraud_risk=fraud_risk,
            compliance_risk=compliance_risk,
            confidence=confidence,
            duplicate_found=duplicate_found,
            amount=float(expense.amount),
            employee_rejection_ratio=rejection_ratio,
        )

        # -------------------------------------------------
        # 7. Approval Workflow (initial routing)
        # -------------------------------------------------

        approval_result = approval_workflow.decide(
            auto_approval,
        )

        # -------------------------------------------------
        # Merge Results
        # -------------------------------------------------

        structured_result["ocr_text"] = ocr_text

        structured_result["policy_status"] = policy_result[
            "status"
        ]
        structured_result["policy_reason"] = policy_result[
            "reason"
        ]
        structured_result["requires_manager_approval"] = (
            policy_result["requires_manager_approval"]
        )

        structured_result["fraud_risk"] = fraud_risk
        structured_result["compliance_risk"] = compliance_risk
        structured_result["confidence"] = confidence
        structured_result["risk_reason"] = policy_result.get(
            "reason"
        )

        structured_result["duplicate_found"] = duplicate_found
        structured_result["duplicate_confidence"] = (
            duplicate_confidence
        )
        structured_result["duplicate_match_fields"] = (
            duplicate_match_fields
        )

        structured_result["ai_recommendation"] = (
            auto_approval.recommendation
        )
        structured_result["required_approval_level"] = (
            auto_approval.required_approval_level
        )
        structured_result["auto_approval_reason"] = (
            auto_approval.reason
        )

        structured_result["approval_status"] = approval_result[
            "approval_status"
        ]
        structured_result["approved_by"] = approval_result[
            "approved_by"
        ]
        structured_result["current_approval_level"] = (
            approval_result["current_approval_level"]
        )

        structured_result["ai_provider"] = engine
        structured_result["ai_fallback"] = fallback
        structured_result["ai_fallback_reason"] = fallback_reason

        return structured_result

    def _employee_rejection_ratio(
        self,
        db: Session,
        employee_id,
    ) -> float:
        """
        Fraction of this employee's past approval actions that
        were rejections - feeds the Auto-Approval Engine's
        employee-history signal.
        """

        actions = (
            db.query(ExpenseApproval)
            .join(
                Expense,
                Expense.id == ExpenseApproval.expense_id,
            )
            .filter(Expense.employee_id == employee_id)
            .all()
        )

        if not actions:
            return 0.0

        rejections = sum(
            1 for a in actions if a.action == "Rejected"
        )

        return rejections / len(actions)


expense_pipeline = ExpensePipeline()
