"""
Test Ollama Receipt Extraction

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pprint import pprint

from app.ai.ollama_service import ollama_service


result = ollama_service.extract_receipt(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg",
)

print("\n========== OLLAMA RESULT ==========\n")

pprint(result)