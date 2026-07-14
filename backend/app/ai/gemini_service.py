"""
Gemini Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json
from pathlib import Path

from google import genai

from app.ai.prompt_templates import RECEIPT_EXTRACTION_PROMPT
from app.config.settings import settings


class GeminiService:
    """
    Gemini AI Service.
    """

    def __init__(self):
        """
        Initialize Gemini Client.
        """

        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY,
        )

    def extract_receipt(
        self,
        image_path: str,
    ) -> dict:
        """
        Extract structured receipt information using Gemini.
        """

        image_file = Path(image_path)

        try:

            # ------------------------------------------
            # Upload Receipt Image
            # ------------------------------------------

            uploaded_file = self.client.files.upload(
                file=image_file,
            )

            # ------------------------------------------
            # Gemini Vision
            # ------------------------------------------

            response = self.client.models.generate_content(
                model="models/gemini-flash-latest",
                contents=[
                    RECEIPT_EXTRACTION_PROMPT,
                    uploaded_file,
                ],
            )

            text = response.text.strip()

            # ------------------------------------------
            # Remove Markdown if Gemini returns it
            # ------------------------------------------

            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            # ------------------------------------------
            # Convert JSON String to Dictionary
            # ------------------------------------------

            return json.loads(text)

        except json.JSONDecodeError as ex:

            raise ValueError(
                f"Gemini returned invalid JSON.\n\n{text}"
            ) from ex

        except Exception as ex:

            raise RuntimeError(
                f"Gemini Extraction Failed.\n{str(ex)}"
            ) from ex


gemini_service = GeminiService()