"""
Expense Pipeline

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from app.ai.gemini_service import gemini_service
from app.ai.groq_service import groq_service
from app.ai.ocr_service import ocr_service
from app.langchain.output_parser import output_parser
from app.workflow.approval_workflow import approval_workflow


class ExpensePipeline:
    """
    AI Processing Pipeline.
    """

    def process_receipt(
        self,
        image_path: str,
    ) -> dict:
        """
        Process receipt through
        OCR -> Gemini -> Groq -> Approval Workflow
        """

        # -------------------------------------------------
        # OCR
        # -------------------------------------------------

        try:

            ocr_text = ocr_service.extract_text(
                image_path,
            )

        except Exception as ex:

            print(f"OCR Error : {ex}")

            ocr_text = ""

        # -------------------------------------------------
        # Gemini
        # -------------------------------------------------

        try:

            gemini_result = gemini_service.extract_receipt(
                image_path,
            )

            structured_result = output_parser.parse(
                gemini_result,
            )

            gemini_success = True

        except Exception as ex:

            print(f"Gemini Error : {ex}")

            gemini_success = False

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
        # Groq Policy Validation
        # -------------------------------------------------

        if (
            gemini_success
            and structured_result.get("total_amount") is not None
            and structured_result.get("expense_category") is not None
        ):

            try:

                policy_result = groq_service.validate_expense(
                    structured_result,
                )

            except Exception as ex:

                print(f"Groq Error : {ex}")

                policy_result = {
                    "status": "UNKNOWN",
                    "reason": "Policy validation failed.",
                    "requires_manager_approval": True,
                }

        else:

            policy_result = {
                "status": "UNKNOWN",
                "reason": (
                    "Policy validation skipped because "
                    "receipt extraction was unsuccessful."
                ),
                "requires_manager_approval": True,
            }

        # -------------------------------------------------
        # Approval Workflow
        # -------------------------------------------------

        try:

            approval_result = approval_workflow.decide(
                policy_status=policy_result["status"],
                requires_manager_approval=policy_result[
                    "requires_manager_approval"
                ],
            )

        except Exception as ex:

            print(f"Approval Error : {ex}")

            approval_result = {
                "approval_status": "Pending Review",
                "approved_by": None,
            }

        # -------------------------------------------------
        # Merge Results
        # -------------------------------------------------

        structured_result["ocr_text"] = ocr_text

        structured_result["policy_status"] = (
            policy_result["status"]
        )

        structured_result["policy_reason"] = (
            policy_result["reason"]
        )

        structured_result["requires_manager_approval"] = (
            policy_result["requires_manager_approval"]
        )

        structured_result["approval_status"] = (
            approval_result["approval_status"]
        )

        structured_result["approved_by"] = (
            approval_result["approved_by"]
        )

        return structured_result


expense_pipeline = ExpensePipeline()