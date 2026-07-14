"""
Groq Test

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pprint import pprint

from app.ai.groq_service import groq_service


expense = {
    "merchant_name": "KFC",
    "expense_category": "Meals",
    "total_amount": 850,
    "currency": "INR",
    "payment_method": "Credit Card",
}

result = groq_service.validate_expense(
    expense,
)

print("\n========== GROQ RESULT ==========\n")

pprint(result)