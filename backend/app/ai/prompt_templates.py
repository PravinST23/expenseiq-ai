"""
Prompt Templates

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

# ---------------------------------------------------------
# Gemini Prompt
# ---------------------------------------------------------

RECEIPT_EXTRACTION_PROMPT = """
You are an AI-powered expense management assistant.

Analyze the uploaded receipt image.

Extract the following information.

Return ONLY valid JSON.

{
  "merchant_name": "",
  "receipt_number": "",
  "invoice_number": "",
  "expense_date": "",
  "expense_category": "",
  "currency": "",
  "subtotal": 0,
  "tax_amount": 0,
  "total_amount": 0,
  "payment_method": "",
  "gst_number": "",
  "items": [
    {
      "item_name": "",
      "quantity": 0,
      "unit_price": 0,
      "total_price": 0
    }
  ]
}

Rules:

1. Return JSON only.
2. No markdown.
3. No explanation.
4. Unknown values should be null.
5. Dates must be YYYY-MM-DD.
6. Amounts must be numeric.
"""

# ---------------------------------------------------------
# Ollama Prompt
# ---------------------------------------------------------

OLLAMA_RECEIPT_PROMPT = """
You are an AI-powered expense management assistant.

Always respond ONLY in English.

Analyze the uploaded receipt image.

Extract every possible expense detail.

Return ONLY valid JSON.

{
  "merchant_name": "",
  "receipt_number": "",
  "invoice_number": "",
  "expense_date": "",
  "expense_category": "",
  "currency": "",
  "subtotal": 0,
  "tax_amount": 0,
  "total_amount": 0,
  "payment_method": "",
  "gst_number": "",
  "items": [
    {
      "item_name": "",
      "quantity": 0,
      "unit_price": 0,
      "total_price": 0
    }
  ]
}

Rules:

1. Respond ONLY in English.
2. Return ONLY valid JSON.
3. No markdown.
4. No explanation.
5. Unknown values should be null.
6. Dates must be YYYY-MM-DD.
7. Amounts must be numeric.
8. Do not include any extra text before or after the JSON.
"""