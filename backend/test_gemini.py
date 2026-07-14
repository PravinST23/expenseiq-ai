"""
Gemini Test

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pprint import pprint

from app.ai.gemini_service import gemini_service


result = gemini_service.extract_receipt(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)

print("\n========== GEMINI RESULT ==========\n")

pprint(result)