"""
Approval API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
APPROVAL_URL = "/api/v1/approvals"


def create_employee(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "Approval Test",
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
            "project_description": "Approval Testing",
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
            "payment_method": "Credit Card",
            "description": "Approval Test",
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_approval_payload(client):

    return {
        "expense_id": create_expense(client),
        "approver_role": "Manager",
        "approver_name": "John Manager",
        "action": "Approved",
        "comments": "Approved for reimbursement",
    }


def test_create_approval(client):

    payload = create_approval_payload(client)

    response = client.post(
        f"{APPROVAL_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["approver_role"] == "Manager"
    assert data["action"] == "Approved"
    assert "id" in data


def test_get_all_approvals(client):

    response = client.get(
        f"{APPROVAL_URL}/",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_approval_by_id(client):

    payload = create_approval_payload(client)

    create = client.post(
        f"{APPROVAL_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    approval_id = create.json()["id"]

    response = client.get(
        f"{APPROVAL_URL}/{approval_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == approval_id


def test_get_approval_history(client):

    payload = create_approval_payload(client)

    create = client.post(
        f"{APPROVAL_URL}/",
        json=payload,
    )

    assert create.status_code == 201

    expense_id = payload["expense_id"]

    response = client.get(
        f"{APPROVAL_URL}/expense/{expense_id}",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_approval(client):

    payload = create_approval_payload(client)

    create = client.post(
        f"{APPROVAL_URL}/",
        json=payload,
    )

    approval_id = create.json()["id"]

    response = client.put(
        f"{APPROVAL_URL}/{approval_id}",
        json={
            "comments": "Updated Comments",
        },
    )

    assert response.status_code == 200
    assert response.json()["comments"] == "Updated Comments"


def test_delete_approval(client):

    payload = create_approval_payload(client)

    create = client.post(
        f"{APPROVAL_URL}/",
        json=payload,
    )

    approval_id = create.json()["id"]

    response = client.delete(
        f"{APPROVAL_URL}/{approval_id}",
    )

    assert response.status_code == 204