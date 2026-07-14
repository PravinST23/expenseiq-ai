"""
OCR Test Script

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from app.ai.ocr_service import ocr_service

text = ocr_service.extract_text(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)

print("\n===== OCR RESULT =====\n")
print(text)