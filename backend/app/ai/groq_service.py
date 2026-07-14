"""
Groq Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json

from groq import Groq

from app.ai.policy_prompt import EXPENSE_POLICY_PROMPT
from app.config.settings import settings


class GroqService:
    """
    Groq AI Service for Expense Policy Validation.
    """

    def __init__(self):
        """
        Initialize Groq Client.
        """

        self.client = Groq(
            api_key=settings.GROQ_API_KEY,
        )

    def validate_expense(
        self,
        expense_data: dict,
    ) -> dict:
        """
        Validate an expense against company policy.
        """

        prompt = f"""
{EXPENSE_POLICY_PROMPT}

Expense Data

{json.dumps(expense_data, indent=4)}
"""

        try:

            response = self.client.chat.completions.create(

                model="llama-3.3-70b-versatile",

                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],

                temperature=0,
            )

            text = response.choices[0].message.content.strip()

            # Remove Markdown if present

            text = (
                text.replace("```json", "")
                .replace("```", "")
                .strip()
            )

            return json.loads(text)

        except json.JSONDecodeError as ex:

            raise ValueError(
                f"Groq returned invalid JSON.\n\n{text}"
            ) from ex

        except Exception as ex:

            raise RuntimeError(
                f"Groq validation failed.\n{str(ex)}"
            ) from ex


groq_service = GroqService()