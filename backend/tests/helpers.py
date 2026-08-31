"""
Shared Test Helpers

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
TEAM_URL = "/api/v1/teams"
EXPENSE_URL = "/api/v1/expenses"
AUTH_URL = "/api/v1/auth"

DEFAULT_PASSWORD = "Password@123"


def create_team(client, hr_head_headers):

    unique = uuid4().hex[:8]

    response = client.post(
        f"{TEAM_URL}/",
        json={"team_code": f"MAC-{unique}", "team_name": f"Team-{unique}"},
        headers=hr_head_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()["id"]


def create_project(client, hr_head_headers, team_id=None):

    unique = uuid4().hex[:6]

    if team_id is None:
        team_id = create_team(client, hr_head_headers)

    response = client.post(
        f"{PROJECT_URL}/",
        json={
            "project_code": f"PRJ{unique}",
            "project_name": f"Project-{unique}",
            "client_name": "Internal",
            "project_description": "Test Project",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "project_manager": "Test Manager",
            "project_budget": 100000,
            "team_id": team_id,
        },
        headers=hr_head_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()["id"]


def create_employee(
    client,
    hr_head_headers,
    *,
    role="EMPLOYEE",
    manager_id=None,
    password=DEFAULT_PASSWORD,
    team_id=None,
    **overrides,
):
    """
    Creates an employee via the real (HR_HEAD-authenticated) API and
    logs them in via the real /auth/login API. Returns
    (employee_dict, auth_headers).
    """

    unique = uuid4().hex[:8]

    payload = {
        "employee_code": f"EMP{unique}",
        "full_name": f"{role} Test User {unique}",
        "email": f"emp{unique}@example.com",
        "department": "IT",
        "designation": role,
        "role": role,
        "password": password,
        "manager_id": manager_id,
        "team_id": team_id,
    }

    payload.update(overrides)

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json=payload,
        headers=hr_head_headers,
    )

    assert response.status_code == 201, response.text

    employee = response.json()

    login = client.post(
        f"{AUTH_URL}/login",
        json={"email": employee["email"], "password": password},
    )

    assert login.status_code == 200, login.text

    token = login.json()["access_token"]

    return employee, {"Authorization": f"Bearer {token}"}


def create_org_chain(client, hr_head_headers):
    """
    Builds a full 3-level manager chain:
    requester -> manager (RM) -> skip_manager (RM's RM), plus one
    CFO who terminates every chain. Returns a dict of
    (employee, headers) tuples keyed by role.
    """

    cfo, cfo_headers = create_employee(client, hr_head_headers, role="CFO")

    skip_manager, skip_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
    )

    manager, manager_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
        manager_id=skip_manager["id"],
    )

    requester, requester_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
        manager_id=manager["id"],
    )

    return {
        "cfo": (cfo, cfo_headers),
        "skip_manager": (skip_manager, skip_headers),
        "manager": (manager, manager_headers),
        "requester": (requester, requester_headers),
    }


def create_expense_for(
    client,
    requester_headers,
    project_id,
    **overrides,
):

    unique = uuid4().hex[:6]

    payload = {
        "expense_number": f"EXP{unique}",
        "project_id": project_id,
        "expense_category": "Travel",
        "merchant_name": "Uber",
        "amount": 450,
        "currency": "INR",
        "expense_date": "2026-07-14",
        "payment_method": "Credit Card",
        "description": "Test expense",
        "is_sensitive": False,
    }

    payload.update(overrides)

    response = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
        headers=requester_headers,
    )

    assert response.status_code == 201, response.text

    return response.json()
