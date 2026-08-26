"""
Reimbursement State Machine Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

PATCH /expenses/{id}/reimbursement requires an authenticated
L2_FINANCE or L3_CFO employee - see app.api.deps.require_roles.
"""

from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
APPROVAL_URL = "/api/v1/approvals"
AUTH_URL = "/api/v1/auth"

APPROVER_PASSWORD = "Approver@123"


def login_as(client, role):

    unique = uuid4().hex[:8]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"REI{unique}",
            "full_name": f"{role} Test User",
            "email": f"rei{unique}@example.com",
            "department": "IT",
            "designation": role,
            "role": role,
            "password": APPROVER_PASSWORD,
        },
    )

    assert response.status_code == 201

    login = client.post(
        f"{AUTH_URL}/login",
        json={
            "email": response.json()["email"],
            "password": APPROVER_PASSWORD,
        },
    )

    assert login.status_code == 200

    token = login.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def _create_expense(client, description="Reimbursement Test"):

    unique = uuid4().hex[:6]

    employee = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "Reimbursement Test",
            "email": f"{unique}@example.com",
            "phone_number": "9999999999",
            "department": "IT",
            "designation": "Developer",
            "manager_name": "Manager",
        },
    ).json()["id"]

    project = client.post(
        f"{PROJECT_URL}/",
        json={
            "project_code": f"PRJ{unique}",
            "project_name": f"Project-{unique}",
            "client_name": "Internal",
            "project_description": "Reimbursement Testing",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "project_manager": "Pravin",
            "project_budget": 100000,
        },
    ).json()["id"]

    return client.post(
        f"{EXPENSE_URL}/",
        json={
            "expense_number": f"EXP{unique}",
            "employee_id": employee,
            "project_id": project,
            "expense_category": "Travel",
            "merchant_name": "Uber",
            "amount": 450,
            "currency": "INR",
            "expense_date": "2026-07-14",
            "payment_method": "Credit Card",
            "description": description,
        },
    ).json()["id"]


def _create_approved_expense(client):

    expense_id = _create_expense(client)

    headers = login_as(client, "L1_MANAGER")

    approval = client.post(
        f"{APPROVAL_URL}/",
        json={
            "expense_id": expense_id,
            "action": "Approved",
            "comments": "Approved for reimbursement",
        },
        headers=headers,
    )

    assert approval.status_code == 201

    return expense_id


def test_reimbursement_defaults_to_pending_before_approval(client):

    expense_id = _create_expense(client, description="Pending Test")

    expense = client.get(f"{EXPENSE_URL}/{expense_id}").json()

    assert expense["reimbursement_state"] == "PENDING"


def test_reimbursement_becomes_approved_after_final_approval(client):

    expense_id = _create_approved_expense(client)

    expense = client.get(f"{EXPENSE_URL}/{expense_id}").json()

    assert expense["status"] == "Approved"
    assert expense["reimbursement_state"] == "APPROVED"


def test_reimbursement_requires_authentication(client):

    expense_id = _create_approved_expense(client)

    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PAID"},
    )

    assert response.status_code == 401


def test_reimbursement_forbidden_for_manager_role(client):
    """
    L1 Manager can approve claims but not mark reimbursements paid -
    that's Finance/CFO's job.
    """

    expense_id = _create_approved_expense(client)

    headers = login_as(client, "L1_MANAGER")

    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=headers,
    )

    assert response.status_code == 403


def test_reimbursement_can_be_marked_paid(client):

    expense_id = _create_approved_expense(client)

    headers = login_as(client, "L2_FINANCE")

    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reimbursement_state"] == "PAID"
    assert data["reimbursement_processed_by"]


def test_reimbursement_cannot_skip_backwards(client):

    expense_id = _create_approved_expense(client)

    headers = login_as(client, "L2_FINANCE")

    client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=headers,
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PENDING"},
        headers=headers,
    )

    assert response.status_code == 400


def test_reimbursement_blocked_before_approval(client):

    expense_id = _create_expense(client, description="Blocked Test")

    headers = login_as(client, "L3_CFO")

    response = client.patch(
        f"{EXPENSE_URL}/{expense_id}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=headers,
    )

    assert response.status_code == 409
