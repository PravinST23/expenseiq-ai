"""
Reimbursement State Machine Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

PATCH /expenses/{id}/reimbursement requires an authenticated CFO -
see app.api.deps.require_roles.
"""

from tests.helpers import create_employee, create_expense_for, create_project

EXPENSE_URL = "/api/v1/expenses"
APPROVAL_URL = "/api/v1/approvals"


def _approve_fully(client, expense, chain_headers_in_order):

    for headers in chain_headers_in_order:

        response = client.post(
            f"{APPROVAL_URL}/",
            json={"expense_id": expense["id"], "action": "Approved"},
            headers=headers,
        )

        assert response.status_code == 201, response.text

        expense = client.get(f"{EXPENSE_URL}/{expense['id']}").json()

        if expense["status"] == "Approved":
            break

    return expense


def _create_approved_expense(client, hr_head_headers):

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

    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    expense = _approve_fully(
        client,
        expense,
        [manager_headers, skip_headers, cfo_headers],
    )

    assert expense["status"] == "Approved"

    return expense, cfo_headers, manager_headers


def test_reimbursement_defaults_to_pending_before_approval(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)

    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    assert expense["reimbursement_state"] == "PENDING"


def test_reimbursement_becomes_approved_after_final_approval(client, hr_head_headers):

    expense, _, _ = _create_approved_expense(client, hr_head_headers)

    fetched = client.get(f"{EXPENSE_URL}/{expense['id']}").json()

    assert fetched["status"] == "Approved"
    assert fetched["reimbursement_state"] == "APPROVED"


def test_reimbursement_requires_authentication(client, hr_head_headers):

    expense, _, _ = _create_approved_expense(client, hr_head_headers)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PAID"},
    )

    assert response.status_code == 401


def test_reimbursement_forbidden_for_manager_role(client, hr_head_headers):
    """
    The requester's own manager can approve claims but not mark
    reimbursements paid - that's the CFO's job.
    """

    expense, _, manager_headers = _create_approved_expense(client, hr_head_headers)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=manager_headers,
    )

    assert response.status_code == 403


def test_reimbursement_can_be_marked_paid(client, hr_head_headers):

    expense, cfo_headers, _ = _create_approved_expense(client, hr_head_headers)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=cfo_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["reimbursement_state"] == "PAID"
    assert data["reimbursement_processed_by"]


def test_reimbursement_cannot_skip_backwards(client, hr_head_headers):

    expense, cfo_headers, _ = _create_approved_expense(client, hr_head_headers)

    client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=cfo_headers,
    )

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PENDING"},
        headers=cfo_headers,
    )

    assert response.status_code == 400


def test_reimbursement_blocked_before_approval(client, hr_head_headers):

    cfo, cfo_headers = create_employee(client, hr_head_headers, role="CFO")

    _, requester_headers = create_employee(client, hr_head_headers)

    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    response = client.patch(
        f"{EXPENSE_URL}/{expense['id']}/reimbursement",
        json={"reimbursement_state": "PAID"},
        headers=cfo_headers,
    )

    assert response.status_code == 409
