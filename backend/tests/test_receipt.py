"""
Receipt API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pathlib import Path
from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
RECEIPT_URL = "/api/v1/receipts"

# Change this path if required
TEST_RECEIPT_PATH = Path(
    "uploads/receipts/45d67a16fc1b4d819eebf73466d2f004.jpg"
)


def create_employee(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "Receipt Test",
            "email": f"{unique}@example.com",
            "phone_number": "9999999999",
            "department": "IT",
            "designation": "Developer",
            "manager_name": "Manager",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_project(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{PROJECT_URL}/",
        json={
            "project_code": f"PRJ{unique}",
            "project_name": f"Project-{unique}",
            "client_name": "Internal",
            "project_description": "Testing",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "project_manager": "Pravin",
            "project_budget": 100000,
        },
    )

    assert response.status_code == 201

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
            "amount": 450,
            "currency": "INR",
            "expense_date": "2026-07-14",
            "payment_method": "Card",
            "description": "Testing",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_upload_receipt(client):

    expense_id = create_expense(client)

    assert TEST_RECEIPT_PATH.exists()

    with open(TEST_RECEIPT_PATH, "rb") as image:

        response = client.post(
            f"{RECEIPT_URL}/upload",
            data={
                "receipt_number": f"RCT{uuid4().hex[:6]}",
                "expense_id": expense_id,
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

    response = client.get(
        f"{RECEIPT_URL}/",
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )