"""
AI Analysis API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pathlib import Path
from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
RECEIPT_URL = "/api/v1/receipts"
AI_URL = "/api/v1/ai-analysis"

TEST_RECEIPT = Path(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)


def create_employee(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "AI Test",
            "email": f"{unique}@example.com",
            "phone_number": "9999999999",
            "department": "IT",
            "designation": "Developer",
            "manager_name": "Manager",
        },
    )

    return response.json()["id"]


def create_project(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{PROJECT_URL}/",
        json={
            "project_code": f"PRJ{unique}",
            "project_name": f"Project-{unique}",
            "client_name": "Internal",
            "project_description": "AI Testing",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "project_manager": "Pravin",
            "project_budget": 100000,
        },
    )

    return response.json()["id"]


def create_expense(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{EXPENSE_URL}/",
        json={
            "expense_number": f"EXP{unique}",
            "employee_id": create_employee(client),
            "project_id": create_project(client),
            "expense_category": "Travel",
            "merchant_name": "Uber",
            "amount": 500,
            "currency": "INR",
            "expense_date": "2026-07-14",
            "payment_method": "Card",
            "description": "AI Test",
        },
    )

    return response.json()["id"]


def upload_receipt(client):

    expense_id = create_expense(client)

    with open(TEST_RECEIPT, "rb") as image:

        response = client.post(
            f"{RECEIPT_URL}/upload",
            data={
                "receipt_number": f"RCT{uuid4().hex[:6]}",
                "expense_id": expense_id,
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

    return expense_id, receipt["id"]


def test_get_all_ai_analysis(client):

    response = client.get(
        f"{AI_URL}/",
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_get_ai_analysis_by_receipt(client):

    _, receipt_id = upload_receipt(client)

    response = client.get(
        f"{AI_URL}/receipt/{receipt_id}",
    )

    assert response.status_code == 200

    data = response.json()

    assert data["receipt_id"] == receipt_id


def test_get_ai_analysis_by_expense(client):

    expense_id, _ = upload_receipt(client)

    response = client.get(
        f"{AI_URL}/expense/{expense_id}",
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_get_ai_analysis_by_id(client):

    _, receipt_id = upload_receipt(client)

    receipt_response = client.get(
        f"{AI_URL}/receipt/{receipt_id}",
    )

    analysis = receipt_response.json()

    analysis_id = analysis["id"]

    response = client.get(
        f"{AI_URL}/{analysis_id}",
    )

    assert response.status_code == 200

    assert response.json()["id"] == analysis_id