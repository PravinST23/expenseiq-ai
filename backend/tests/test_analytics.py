"""
Analytics API Smoke Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

ANALYTICS_URL = "/api/v1/analytics"


def test_spend_by_category(client):

    response = client.get(f"{ANALYTICS_URL}/spend-by-category")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_spend_by_employee(client):

    response = client.get(f"{ANALYTICS_URL}/spend-by-employee")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_spend_by_project(client):

    response = client.get(f"{ANALYTICS_URL}/spend-by-project")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_approval_status_summary(client):

    response = client.get(
        f"{ANALYTICS_URL}/approval-status-summary"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_reimbursement_liability(client):

    response = client.get(
        f"{ANALYTICS_URL}/reimbursement-liability"
    )

    assert response.status_code == 200

    data = response.json()

    assert "by_state" in data
    assert "outstanding_liability" in data


def test_ai_accuracy(client):

    response = client.get(f"{ANALYTICS_URL}/ai-accuracy")

    assert response.status_code == 200

    data = response.json()

    assert "total_expenses" in data
    assert "duplicate_rate" in data


def test_overview(client):

    response = client.get(f"{ANALYTICS_URL}/overview")

    assert response.status_code == 200

    data = response.json()

    assert "total_employees" in data
    assert "total_expenses" in data
