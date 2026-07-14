"""
OCR Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pathlib import Path

from PIL import Image
import pytesseract


class OCRService:

    def extract_text(
        self,
        image_path: str,
    ) -> str:

        image = Image.open(
            Path(image_path)
        )

        text = pytesseract.image_to_string(
            image,
            lang="eng",
        )

        return text.strip()


ocr_service = OCRService()