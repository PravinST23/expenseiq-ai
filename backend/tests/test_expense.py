"""
Expense API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Creating an expense requires authentication - the claim is always
submitted as the logged-in employee (employee_id in the body is
ignored/overridden).
"""

from uuid import uuid4

from tests.helpers import create_employee, create_project

EXPENSE_URL = "/api/v1/expenses"


def create_expense_payload(client, hr_head_headers):

    unique = uuid4().hex[:6]

    requester, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    payload = {
        "expense_number": f"EXP{unique}",
        "employee_id": requester["id"],
        "project_id": project_id,
        "expense_category": "Travel",
        "merchant_name": "Uber",
        "amount": 450.75,
        "currency": "INR",
        "expense_date": "2026-07-14",
        "payment_method": "Credit Card",
        "description": "Travel to client office",
    }

    return payload, requester_headers


def test_create_expense_requires_authentication(client, hr_head_headers):

    payload, _ = create_expense_payload(client, hr_head_headers)

    response = client.post(f"{EXPENSE_URL}/", json=payload)

    assert response.status_code == 401


def test_create_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    response = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert response.status_code == 201

    data = response.json()

    assert data["expense_number"] == payload["expense_number"]
    assert data["merchant_name"] == payload["merchant_name"]
    assert data["employee_id"] == payload["employee_id"]
    assert "id" in data


def test_create_expense_ignores_forged_employee_id(client, hr_head_headers):
    """
    Even if the body names a different employee_id, the server must
    submit the claim as whoever is actually authenticated.
    """

    payload, headers = create_expense_payload(client, hr_head_headers)

    forged_requester, _ = create_employee(client, hr_head_headers)
    payload["employee_id"] = forged_requester["id"]

    response = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.json()["employee_id"] != forged_requester["id"]


def test_get_all_expenses(client):

    response = client.get(f"{EXPENSE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_expense_by_id(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.get(f"{EXPENSE_URL}/{expense_id}")

    assert response.status_code == 200
    assert response.json()["id"] == expense_id


def test_update_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.put(
        f"{EXPENSE_URL}/{expense_id}",
        json={"merchant_name": "Ola Cabs"},
    )

    assert response.status_code == 200
    assert response.json()["merchant_name"] == "Ola Cabs"


def test_delete_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.delete(f"{EXPENSE_URL}/{expense_id}")

    assert response.status_code == 204
