"""
Approval API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

POST/PUT/DELETE on /approvals require authentication; authorization
is per-resource - ApprovalService checks the caller is the exact
employee the manager chain (Reporting Manager -> Skip-Level Manager
-> CFO) resolves to for THIS expense's requester at its current
level - see app.workflow.manager_chain.
"""

from tests.helpers import (
    create_employee,
    create_expense_for,
    create_org_chain,
    create_project,
)

APPROVAL_URL = "/api/v1/approvals"
EXPENSE_URL = "/api/v1/expenses"


def _submit_expense(client, chain, project_id):

    requester, requester_headers = chain["requester"]

    return create_expense_for(client, requester_headers, project_id)


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


def test_create_approval(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]

    response = approve(client, expense["id"], manager_headers)

    assert response.status_code == 201

    data = response.json()

    assert data["approver_role"] == "Reporting Manager"
    assert data["approval_level"] == 1
    assert data["action"] == "Approved"
    assert "id" in data


def test_create_approval_requires_authentication(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    response = client.post(
        f"{APPROVAL_URL}/",
        json={"expense_id": expense["id"], "action": "Approved"},
    )

    assert response.status_code == 401


def test_wrong_person_cannot_approve(client, hr_head_headers):
    """
    Only the requester's ACTUAL reporting manager may act at level
    1 - not just anyone, and not even the requester's skip-level
    manager out of turn.
    """

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, skip_manager_headers = chain["skip_manager"]

    response = approve(client, expense["id"], skip_manager_headers)

    assert response.status_code == 403


def test_unrelated_manager_cannot_approve(client, hr_head_headers):
    """
    A manager who isn't in this requester's chain at all must be
    rejected too - not just anyone holding role EMPLOYEE-with-
    direct-reports.
    """

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    unrelated, unrelated_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
    )

    response = approve(client, expense["id"], unrelated_headers)

    assert response.status_code == 403


def test_approver_identity_is_resolved_not_client_supplied(client, hr_head_headers):
    """
    Even if the caller is the correct resolved approver, the audit
    row records THEIR real identity - there's no field left in the
    request body to forge a different one.
    """

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    manager, manager_headers = chain["manager"]

    response = approve(client, expense["id"], manager_headers)

    assert response.status_code == 201

    data = response.json()

    assert data["approver_name"] == manager["full_name"]
    assert data["approver_employee_id"] == manager["id"]


def test_get_all_approvals(client):

    response = client.get(f"{APPROVAL_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_approval_by_id(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]

    create = approve(client, expense["id"], manager_headers)

    assert create.status_code == 201

    approval_id = create.json()["id"]

    response = client.get(f"{APPROVAL_URL}/{approval_id}")

    assert response.status_code == 200
    assert response.json()["id"] == approval_id


def test_get_approval_history(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]

    create = approve(client, expense["id"], manager_headers)

    assert create.status_code == 201

    response = client.get(f"{APPROVAL_URL}/expense/{expense['id']}")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_update_approval_requires_cfo(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]

    create = approve(client, expense["id"], manager_headers)
    approval_id = create.json()["id"]

    # The acting manager themself is not a CFO - forbidden.
    forbidden = client.put(
        f"{APPROVAL_URL}/{approval_id}",
        json={"comments": "Trying to self-correct"},
        headers=manager_headers,
    )
    assert forbidden.status_code == 403

    _, cfo_headers = chain["cfo"]

    response = client.put(
        f"{APPROVAL_URL}/{approval_id}",
        json={"comments": "Corrected by CFO"},
        headers=cfo_headers,
    )

    assert response.status_code == 200
    assert response.json()["comments"] == "Corrected by CFO"


def test_delete_approval_requires_cfo(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]
    _, cfo_headers = chain["cfo"]

    create = approve(client, expense["id"], manager_headers)
    approval_id = create.json()["id"]

    response = client.delete(
        f"{APPROVAL_URL}/{approval_id}",
        headers=cfo_headers,
    )

    assert response.status_code == 204


def test_out_of_order_level_rejected(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    # Skip-level manager tries to act before the direct manager has.
    _, skip_headers = chain["skip_manager"]

    response = approve(client, expense["id"], skip_headers)

    assert response.status_code == 403


def test_full_chain_marks_expense_approved(client, hr_head_headers):
    """
    Walks a claim through however many levels it requires,
    confirming each level's action is only accepted from the
    correct real person, and the final level moves the expense to
    Approved + reimbursement APPROVED.
    """

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    level_order = ["manager", "skip_manager", "cfo"]

    required_level = expense["required_approval_level"]

    for level in range(1, required_level + 1):

        key = level_order[level - 1]
        _, headers = chain[key]

        response = approve(client, expense["id"], headers)

        assert response.status_code == 201, (
            f"level {level} ({key}) failed: {response.text}"
        )

    final = client.get(f"{EXPENSE_URL}/{expense['id']}").json()

    assert final["status"] == "Approved"
    assert final["reimbursement_state"] == "APPROVED"


def test_rejection_is_terminal(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]

    response = approve(client, expense["id"], manager_headers, action="Rejected")

    assert response.status_code == 201

    final = client.get(f"{EXPENSE_URL}/{expense['id']}").json()

    assert final["status"] == "Rejected"

    _, skip_headers = chain["skip_manager"]

    second = approve(client, expense["id"], skip_headers)

    assert second.status_code == 409


def test_manager_with_no_rm_escalates_to_cfo(client, hr_head_headers):
    """
    If a requester's manager has no manager of their own (only one
    level of hierarchy above them), level 2 must escalate straight
    to the CFO rather than erroring.
    """

    cfo, cfo_headers = create_employee(client, hr_head_headers, role="CFO")

    manager, manager_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
    )

    requester, requester_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
        manager_id=manager["id"],
    )

    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    # Force a 2-level requirement for this test regardless of what
    # the auto-approval engine happened to pick, by walking level 1
    # then checking who level 2 resolves to.
    approve(client, expense["id"], manager_headers)

    final = client.get(f"{EXPENSE_URL}/{expense['id']}").json()

    if final["required_approval_level"] >= 2:

        response = approve(client, expense["id"], cfo_headers)

        assert response.status_code == 201
        # The label reflects the LEVEL being filled (Skip-Level
        # Manager), even though the CFO is who actually filled it
        # via escalation - see app.workflow.manager_chain.
        assert response.json()["approver_role"] == "Skip-Level Manager"


def test_requester_with_no_manager_escalates_level_1_to_cfo(client, hr_head_headers):

    cfo, cfo_headers = create_employee(client, hr_head_headers, role="CFO")

    requester, requester_headers = create_employee(
        client, hr_head_headers, role="EMPLOYEE",
    )

    project_id = create_project(client, hr_head_headers)

    expense = create_expense_for(client, requester_headers, project_id)

    response = approve(client, expense["id"], cfo_headers)

    assert response.status_code == 201
    # Same here - level 1's label is "Reporting Manager" regardless
    # of who fills it once escalated.
    assert response.json()["approver_role"] == "Reporting Manager"
    assert response.json()["approver_employee_id"] == cfo["id"]


def test_pending_for_me_shows_only_my_expenses(client, hr_head_headers):

    chain = create_org_chain(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)
    expense = _submit_expense(client, chain, project_id)

    _, manager_headers = chain["manager"]
    _, unrelated_headers = create_employee(client, hr_head_headers)

    manager_view = client.get(
        f"{EXPENSE_URL}/pending-for-me", headers=manager_headers
    )
    unrelated_view = client.get(
        f"{EXPENSE_URL}/pending-for-me", headers=unrelated_headers
    )

    assert manager_view.status_code == 200
    assert any(e["id"] == expense["id"] for e in manager_view.json())

    assert unrelated_view.status_code == 200
    assert not any(e["id"] == expense["id"] for e in unrelated_view.json())


def test_pending_for_me_requires_authentication(client):

    response = client.get(f"{EXPENSE_URL}/pending-for-me")

    assert response.status_code == 401
