"""
Duplicate Fraud Detector Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

from app.database.session import SessionLocal
from app.models.expense import Expense
from app.services.duplicate_check_service import duplicate_check_service
from tests.helpers import create_employee, create_expense_for, create_project

DUPLICATE_URL = "/api/v1/duplicate-checks"


def test_no_duplicate_for_distinct_expenses(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    unique = uuid4().hex[:8]

    # Merchant name starts with the unique token (not just
    # appended) so it can never be a near-superstring of a
    # leftover row from a previous run of this same test - the
    # shared dev database is never torn down between runs.
    expense = create_expense_for(
        client,
        requester_headers,
        project_id,
        merchant_name=f"{unique} Standalone Merchant",
        amount=100 + (int(unique[:4], 16) % 5000),
        expense_date="2020-01-01",
    )

    db = SessionLocal()

    try:
        expense_row = db.query(Expense).filter(
            Expense.id == expense["id"]
        ).first()

        result = duplicate_check_service.run_check(db, expense_row)

        assert result.duplicate_found is False

    finally:
        db.close()


def test_matching_merchant_amount_date_flags_duplicate(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    unique = uuid4().hex[:8]

    common = {
        "merchant_name": f"The Duplicate Diner {unique}",
        "amount": 1234.50,
        "expense_date": "2026-08-15",
    }

    original = create_expense_for(
        client, requester_headers, project_id, **common
    )

    duplicate = create_expense_for(
        client, requester_headers, project_id, **common
    )

    db = SessionLocal()

    try:
        expense_row = db.query(Expense).filter(
            Expense.id == duplicate["id"]
        ).first()

        result = duplicate_check_service.run_check(db, expense_row)

        assert result.duplicate_found is True
        assert str(result.matched_expense_id) == original["id"]
        assert "merchant_name" in result.match_fields
        assert "amount" in result.match_fields
        assert "expense_date" in result.match_fields

    finally:
        db.close()

    response = client.get(f"{DUPLICATE_URL}/expense/{duplicate['id']}")

    assert response.status_code == 200
    assert response.json()["duplicate_found"] is True


def test_get_all_duplicate_checks(client):

    response = client.get(f"{DUPLICATE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
