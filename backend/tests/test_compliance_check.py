"""
Compliance Check API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import uuid4

from app.database.session import SessionLocal
from app.services.compliance_check_service import compliance_check_service

COMPLIANCE_URL = "/api/v1/compliance-checks"
EMPLOYEE_URL = "/api/v1/employees"
PROJECT_URL = "/api/v1/projects"
EXPENSE_URL = "/api/v1/expenses"


def _create_expense(client):

    unique = uuid4().hex[:6]

    employee = client.post(
        f"{EMPLOYEE_URL}/",
        json={
            "employee_code": f"EMP{unique}",
            "full_name": "Compliance Test",
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
            "project_description": "Compliance Testing",
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
            "payment_method": "Card",
            "description": "Compliance Test",
        },
    ).json()["id"]


def test_get_all_compliance_checks(client):

    response = client.get(f"{COMPLIANCE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_compliance_check_by_expense_not_found(client):

    response = client.get(f"{COMPLIANCE_URL}/expense/{uuid4()}")

    assert response.status_code == 404


def test_compliance_check_upsert_creates_then_updates(client):

    expense_id = _create_expense(client)

    db = SessionLocal()

    try:
        created = compliance_check_service.upsert(
            db,
            expense_id=expense_id,
            policy_status="PASS",
            policy_reason="Within policy",
            ai_model="gemini",
        )

        assert created.policy_status == "PASS"

        updated = compliance_check_service.upsert(
            db,
            expense_id=expense_id,
            policy_status="FAIL",
            policy_reason="Exceeds category cap",
            ai_model="ollama",
        )

        assert updated.id == created.id
        assert updated.policy_status == "FAIL"
        assert updated.ai_model == "ollama"

    finally:
        db.close()

    response = client.get(f"{COMPLIANCE_URL}/expense/{expense_id}")

    assert response.status_code == 200
    assert response.json()["policy_status"] == "FAIL"
