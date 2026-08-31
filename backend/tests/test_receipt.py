"""
Receipt API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

import os
from pathlib import Path
from uuid import uuid4

import pytest

from tests.helpers import create_employee, create_expense_for, create_project

RECEIPT_URL = "/api/v1/receipts"

# Change this path if required
TEST_RECEIPT_PATH = Path(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)


@pytest.mark.skipif(
    os.getenv("CI") == "true",
    reason=(
        "Requires live Gemini/Groq API keys and a local Ollama "
        "runtime - not available in CI."
    ),
)
def test_upload_receipt(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    assert TEST_RECEIPT_PATH.exists()

    with open(TEST_RECEIPT_PATH, "rb") as image:

        response = client.post(
            f"{RECEIPT_URL}/upload",
            data={
                "receipt_number": f"RCT{uuid4().hex[:6]}",
                "expense_id": expense["id"],
            },
            files={
                "file": (
                    TEST_RECEIPT_PATH.name,
                    image,
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["receipt_number"] is not None
    assert data["upload_status"] is not None


def test_get_all_receipts(client):

    response = client.get(f"{RECEIPT_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
