"""
Groq Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import json

from groq import Groq

from app.ai.policy_prompt import EXPENSE_POLICY_PROMPT
from app.config.settings import settings

# llama-3.3-70b-versatile was retired from Groq's catalog after the
# mid-term checkpoint; openai/gpt-oss-120b is the current closest
# equivalent (large, fast, reliable structured JSON output) and is
# still available on Groq's free tier. See docs/DEVIATIONS.md.
GROQ_MODEL = "openai/gpt-oss-120b"

# Groq has generally been fast (<2s) but a client-level timeout keeps
# a stalled connection from hanging the whole pipeline indefinitely.
GROQ_TIMEOUT_SECONDS = 20


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
            timeout=GROQ_TIMEOUT_SECONDS,
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

                model=GROQ_MODEL,

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