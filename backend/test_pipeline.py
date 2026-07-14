"""
Expense Pipeline Test

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pprint import pprint

from app.langchain.expense_pipeline import expense_pipeline

result = expense_pipeline.process_receipt(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)

print("\n========== COMPLETE PIPELINE ==========\n")

pprint(result)