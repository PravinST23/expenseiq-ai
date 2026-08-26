"""
Duplicate Fraud Detector Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

from app.database.session import SessionLocal
from app.models.expense import Expense
from app.services.duplicate_check_service import duplicate_check_service

EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"
DUPLICATE_URL = "/api/v1/duplicate-checks"


def create_employee(client):

    unique = uuid4().hex[:6]

    response = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "Duplicate Test",
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
            "project_description": "Duplicate Testing",
            "start_date": "2026-07-01",
            "end_date": "2026-12-31",
            "project_manager": "Pravin",
            "project_budget": 100000,
        },
    )

    assert response.status_code == 201

    return response.json()["id"]


def create_expense(client, employee_id, project_id, **overrides):

    unique = uuid4().hex[:6]

    payload = {
        "expense_number": f"EXP{unique}",
        "employee_id": employee_id,
        "project_id": project_id,
        "expense_category": "Travel",
        "merchant_name": "Cafe Coffee Day",
        "amount": 620,
        "currency": "INR",
        "expense_date": "2026-08-01",
        "payment_method": "Credit Card",
        "description": "Duplicate Test",
    }

    payload.update(overrides)

    response = client.post(
        f"{EXPENSE_URL}/",
        json=payload,
    )

    assert response.status_code == 201

    return response.json()["id"]


def test_no_duplicate_for_distinct_expenses(client):

    employee_id = create_employee(client)
    project_id = create_project(client)

    unique = uuid4().hex[:8]

    # Merchant name starts with the unique token (not just
    # appended) so it can never be a near-superstring of a
    # leftover row from a previous run of this same test - the
    # shared dev database is never torn down between runs.
    expense_id = create_expense(
        client,
        employee_id,
        project_id,
        merchant_name=f"{unique} Standalone Merchant",
        amount=100 + (int(unique[:4], 16) % 5000),
        expense_date="2020-01-01",
    )

    db = SessionLocal()

    try:
        expense = db.query(Expense).filter(
            Expense.id == expense_id
        ).first()

        result = duplicate_check_service.run_check(db, expense)

        assert result.duplicate_found is False

    finally:
        db.close()


def test_matching_merchant_amount_date_flags_duplicate(client):

    employee_id = create_employee(client)
    project_id = create_project(client)

    unique = uuid4().hex[:8]

    common = {
        "merchant_name": f"The Duplicate Diner {unique}",
        "amount": 1234.50,
        "expense_date": "2026-08-15",
    }

    original_id = create_expense(
        client,
        employee_id,
        project_id,
        **common,
    )

    duplicate_id = create_expense(
        client,
        employee_id,
        project_id,
        **common,
    )

    db = SessionLocal()

    try:
        expense = db.query(Expense).filter(
            Expense.id == duplicate_id
        ).first()

        result = duplicate_check_service.run_check(db, expense)

        assert result.duplicate_found is True
        assert str(result.matched_expense_id) == original_id
        assert "merchant_name" in result.match_fields
        assert "amount" in result.match_fields
        assert "expense_date" in result.match_fields

    finally:
        db.close()

    response = client.get(
        f"{DUPLICATE_URL}/expense/{duplicate_id}",
    )

    assert response.status_code == 200
    assert response.json()["duplicate_found"] is True


def test_get_all_duplicate_checks(client):

    response = client.get(f"{DUPLICATE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
