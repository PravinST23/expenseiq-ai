"""
Expense Pipeline

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from app.ai.gemini_service import gemini_service
from app.ai.ocr_service import ocr_service
from app.langchain.output_parser import output_parser


class ExpensePipeline:
    """
    AI Processing Pipeline.
    """

    def process_receipt(
        self,
        image_path: str,
    ) -> dict:
        """
        Process receipt using OCR + Gemini.
        """

        # -------------------------------------
        # OCR
        # -------------------------------------

        ocr_text = ocr_service.extract_text(
            image_path,
        )

        # -------------------------------------
        # Gemini Vision
        # -------------------------------------

        gemini_result = gemini_service.extract_receipt(
            image_path,
        )

        # -------------------------------------
        # Parse Output
        # -------------------------------------

        structured_result = output_parser.parse(
            gemini_result,
        )

        structured_result["ocr_text"] = ocr_text

        return structured_result


expense_pipeline = ExpensePipeline()