"""
Ollama Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json

import ollama

from app.ai.prompt_templates import OLLAMA_RECEIPT_PROMPT
from app.config.settings import settings


class OllamaService:
    """
    Offline Receipt Extraction using Ollama.
    """

    def __init__(self):

        self.host = settings.OLLAMA_HOST
        self.model = settings.OLLAMA_MODEL

        self.client = ollama.Client(
            host=self.host,
        )

    def extract_receipt(
        self,
        image_path: str,
    ) -> dict:
        """
        Extract receipt information using Ollama.
        """

        try:

            response = self.client.generate(
                model=self.model,
                prompt=OLLAMA_RECEIPT_PROMPT,
                images=[image_path],
            )

            response_text = response["response"].strip()

            print("\n========== OLLAMA RAW RESPONSE ==========\n")
            print(response_text)
            print("\n=========================================\n")

            # If response is empty
            if not response_text:
                raise RuntimeError(
                    "Ollama returned an empty response."
                )

            # Extract JSON if surrounded by extra text
            start = response_text.find("{")
            end = response_text.rfind("}")

            if start != -1 and end != -1:

                response_text = response_text[
                    start:end + 1
                ]

            return json.loads(
                response_text,
            )

        except Exception as ex:

            raise RuntimeError(
                f"Ollama Extraction Failed.\n{ex}"
            ) from ex


ollama_service = OllamaService()