"""
Compliance Check API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

from app.database.session import SessionLocal
from app.services.compliance_check_service import compliance_check_service
from tests.helpers import create_employee, create_expense_for, create_project

COMPLIANCE_URL = "/api/v1/compliance-checks"


def _create_expense(client, hr_head_headers):

    _, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    return create_expense_for(client, requester_headers, project_id)


def test_get_all_compliance_checks(client):

    response = client.get(f"{COMPLIANCE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_compliance_check_by_expense_not_found(client):

    response = client.get(f"{COMPLIANCE_URL}/expense/{uuid4()}")

    assert response.status_code == 404


def test_compliance_check_upsert_creates_then_updates(client, hr_head_headers):

    expense = _create_expense(client, hr_head_headers)

    db = SessionLocal()

    try:
        created = compliance_check_service.upsert(
            db,
            expense_id=expense["id"],
            policy_status="PASS",
            policy_reason="Within policy",
            ai_model="gemini",
        )

        assert created.policy_status == "PASS"

        updated = compliance_check_service.upsert(
            db,
            expense_id=expense["id"],
            policy_status="FAIL",
            policy_reason="Exceeds category cap",
            ai_model="ollama",
        )

        assert updated.id == created.id
        assert updated.policy_status == "FAIL"
        assert updated.ai_model == "ollama"

    finally:
        db.close()

    response = client.get(f"{COMPLIANCE_URL}/expense/{expense['id']}")

    assert response.status_code == 200
    assert response.json()["policy_status"] == "FAIL"
