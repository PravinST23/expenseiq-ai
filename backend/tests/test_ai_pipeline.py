"""
AI Analysis API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import os
from pathlib import Path
from uuid import uuid4

import pytest

from tests.helpers import create_employee, create_expense_for, create_project

# These tests drive the full AI pipeline (Gemini / Groq / Ollama)
# with real network / on-device calls, so they only run when a
# developer explicitly runs them locally - CI skips them (no live
# API keys or Ollama runtime available on the runner) and relies on
# the mocked test_hybrid_router.py / test_auto_approval_engine.py
# suites for that logic instead.
pytestmark = pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason=(
        "Requires live Gemini/Groq API keys and a local Ollama "
        "runtime - not available in CI."
    ),
)

RECEIPT_URL = "/api/v1/receipts"
AI_URL = "/api/v1/ai-analysis"

TEST_RECEIPT = Path(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)


def upload_receipt(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    with open(TEST_RECEIPT, "rb") as image:

        response = client.post(
            f"{RECEIPT_URL}/upload",
            data={
                "receipt_number": f"RCT{uuid4().hex[:6]}",
                "expense_id": expense["id"],
            },
            files={
                "file": (
                    TEST_RECEIPT.name,
                    image,
                    "image/jpeg",
                )
            },
        )

    receipt = response.json()

    return expense["id"], receipt["id"]


def test_get_all_ai_analysis(client):

    response = client.get(f"{AI_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_ai_analysis_by_receipt(client, hr_head_headers):

    _, receipt_id = upload_receipt(client, hr_head_headers)

    response = client.get(f"{AI_URL}/receipt/{receipt_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["receipt_id"] == receipt_id


def test_get_ai_analysis_by_expense(client, hr_head_headers):

    expense_id, _ = upload_receipt(client, hr_head_headers)

    response = client.get(f"{AI_URL}/expense/{expense_id}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_ai_analysis_by_id(client, hr_head_headers):

    _, receipt_id = upload_receipt(client, hr_head_headers)

    receipt_response = client.get(f"{AI_URL}/receipt/{receipt_id}")

    analysis = receipt_response.json()

    analysis_id = analysis["id"]

    response = client.get(f"{AI_URL}/{analysis_id}")

    assert response.status_code == 200
    assert response.json()["id"] == analysis_id
