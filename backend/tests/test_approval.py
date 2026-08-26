"""
Approval API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

POST/PUT/DELETE on /approvals require an authenticated employee
holding an approval role (L1_MANAGER/L2_FINANCE/L3_CFO) - see
app.api.deps.require_roles. The authenticated identity, not the
request body, determines who/what role the approval is recorded as.
"""

from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
APPROVAL_URL = "/api/v1/approvals"
AUTH_URL = "/api/v1/auth"

APPROVER_PASSWORD = "Approver@123"


def login_as(client, role):
    """
    Create an employee with the given approval role and a known
    password, log in, and return (auth_headers, employee_id).
    """

    unique = uuid4().hex[:8]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"APR{unique}",
            "full_name": f"{role} Test User",
            "email": f"apr{unique}@example.com",
            "department": "IT",
            "designation": role,
            "role": role,
            "password": APPROVER_PASSWORD,
        },
    )

    assert response.status_code == 201

    employee_id = response.json()["id"]

    login = client.post(
        f"{AUTH_URL}/login",
        json={
            "email": response.json()["email"],
            "password": APPROVER_PASSWORD,
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}, employee_id


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


def create_expense(client, is_sensitive=False):

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
            "is_sensitive": is_sensitive,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def approve(client, expense_id, headers, action="Approved"):

    return client.post(
        f"{APPROVAL_URL}/",
        json={
            "expense_id": expense_id,
            "action": action,
            "comments": f"{action} via test",
        },
        headers=headers,
    )


def test_create_approval(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    response = approve(client, expense_id, headers)

    assert response.status_code == 201

    data = response.json()

    assert data["approver_role"] == "L1_MANAGER"
    assert data["approval_level"] == 1
    assert data["action"] == "Approved"
    assert "id" in data


def test_create_approval_requires_authentication(client):

    expense_id = create_expense(client)

    response = client.post(
        f"{APPROVAL_URL}/",
        json={"expense_id": expense_id, "action": "Approved"},
    )

    assert response.status_code == 401


def test_employee_role_cannot_approve(client):

    headers, _ = login_as(client, "EMPLOYEE")
    expense_id = create_expense(client)

    response = approve(client, expense_id, headers)

    assert response.status_code == 403


def test_approver_identity_is_taken_from_token_not_body(client):
    """
    Even if the request body claims a different role/name, the
    server must use the authenticated employee's real identity.
    """

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    response = client.post(
        f"{APPROVAL_URL}/",
        json={
            "expense_id": expense_id,
            "approver_role": "L3_CFO",
            "approver_name": "Forged Name",
            "action": "Approved",
        },
        headers=headers,
    )

    assert response.status_code == 201

    data = response.json()

    assert data["approver_role"] == "L1_MANAGER"
    assert data["approver_name"] != "Forged Name"


def test_get_all_approvals(client):

    response = client.get(
        f"{APPROVAL_URL}/",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_approval_by_id(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    create = approve(client, expense_id, headers)

    assert create.status_code == 201

    approval_id = create.json()["id"]

    response = client.get(
        f"{APPROVAL_URL}/{approval_id}",
    )

    assert response.status_code == 200
    assert response.json()["id"] == approval_id


def test_get_approval_history(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    create = approve(client, expense_id, headers)

    assert create.status_code == 201

    response = client.get(
        f"{APPROVAL_URL}/expense/{expense_id}",
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_approval(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    create = approve(client, expense_id, headers)

    approval_id = create.json()["id"]

    response = client.put(
        f"{APPROVAL_URL}/{approval_id}",
        json={"comments": "Updated Comments"},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["comments"] == "Updated Comments"


def test_update_approval_requires_authentication(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    create = approve(client, expense_id, headers)

    approval_id = create.json()["id"]

    response = client.put(
        f"{APPROVAL_URL}/{approval_id}",
        json={"comments": "No auth"},
    )

    assert response.status_code == 401


def test_delete_approval(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    create = approve(client, expense_id, headers)

    approval_id = create.json()["id"]

    response = client.delete(
        f"{APPROVAL_URL}/{approval_id}",
        headers=headers,
    )

    assert response.status_code == 204


def test_out_of_order_level_rejected(client):

    headers, _ = login_as(client, "L2_FINANCE")
    expense_id = create_expense(client)

    response = approve(client, expense_id, headers)

    assert response.status_code == 409


def test_single_level_approval_marks_expense_approved(client):

    headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    response = approve(client, expense_id, headers)

    assert response.status_code == 201

    expense = client.get(
        f"{EXPENSE_URL}/{expense_id}",
    ).json()

    assert expense["status"] == "Approved"
    assert expense["reimbursement_state"] == "APPROVED"


def test_rejection_is_terminal(client):

    l1_headers, _ = login_as(client, "L1_MANAGER")
    expense_id = create_expense(client)

    response = approve(client, expense_id, l1_headers, action="Rejected")

    assert response.status_code == 201

    expense = client.get(
        f"{EXPENSE_URL}/{expense_id}",
    ).json()

    assert expense["status"] == "Rejected"

    l2_headers, _ = login_as(client, "L2_FINANCE")

    second = approve(client, expense_id, l2_headers)

    assert second.status_code == 409
