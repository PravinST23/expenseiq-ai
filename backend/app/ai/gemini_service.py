"""
Gemini Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json
from pathlib import Path

from google import genai
from google.genai import types

from app.ai.prompt_templates import RECEIPT_EXTRACTION_PROMPT
from app.config.settings import settings

# Without an explicit timeout, a stalled network path can hang this
# call forever - which also silently defeats the Hybrid Router's
# fallback-to-Ollama logic, since a hang never raises an exception
# for it to catch. 30s is generous for a single receipt image.
GEMINI_TIMEOUT_MS = 30_000

# Gemini 2.5 Flash (the model named in the approved proposal) has
# since been retired for this API key ("no longer available to new
# users"), and the "-latest" alias currently times out. 3.5 Flash is
# the closest available same-tier multimodal model - verified
# working end-to-end on 2026-08-26. See docs/DEVIATIONS.md.
GEMINI_MODEL = "models/gemini-3.5-flash"


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
            http_options=types.HttpOptions(
                timeout=GEMINI_TIMEOUT_MS,
            ),
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
                model=GEMINI_MODEL,
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