"""
Expense API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"


def create_employee(client):

    unique = uuid4().hex[:6]

    payload = {
        "employee_code": f"EMP{unique}",
        "full_name": "Expense Test Employee",
        "email": f"employee{unique}@example.com",
        "phone_number": "9876543210",
        "department": "Engineering",
        "designation": "Software Engineer",
        "manager_name": "John Manager",
    }

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_project(client):

    unique = uuid4().hex[:6]

    payload = {
        "project_code": f"PRJ{unique}",
        "project_name": f"ExpenseIQ-{unique}",
        "client_name": "Internal",
        "project_description": "Expense Test Project",
        "start_date": "2026-07-01",
        "end_date": "2026-12-31",
        "project_manager": "Pravin",
        "project_budget": 100000,
    }

    response = client.post(
        f"{PROJECT_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_expense_payload(client):

    unique = uuid4().hex[:6]

    return {
        "expense_number": f"EXP{unique}",
        "employee_id": create_employee(client),
        "project_id": create_project(client),
        "expense_category": "Travel",
        "merchant_name": "Uber",
        "amount": 450.75,
        "currency": "INR",
        "expense_date": "2026-07-14",
        "payment_method": "Credit Card",
        "description": "Travel to client office",
    }


def test_create_expense(client):

    payload = create_expense_payload(client)

    response = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["expense_number"] == payload["expense_number"]
    assert data["merchant_name"] == payload["merchant_name"]
    assert "id" in data


def test_get_all_expenses(client):

    response = client.get(
        f"{EXPENSE_URL}/",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_expense_by_id(client):

    payload = create_expense_payload(client)

    create = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.get(
        f"{EXPENSE_URL}/{expense_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == expense_id


def test_update_expense(client):

    payload = create_expense_payload(client)

    create = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    expense_id = create.json()["id"]

    update_payload = {
        "merchant_name": "Ola Cabs",
    }

    response = client.put(
        f"{EXPENSE_URL}/{expense_id}",
        json=update_payload,
    )

    assert response.status_code == 200
    assert response.json()["merchant_name"] == "Ola Cabs"


def test_delete_expense(client):

    payload = create_expense_payload(client)

    create = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.delete(
        f"{EXPENSE_URL}/{expense_id}",
    )

    assert response.status_code == 204