"""
Expense API Tests

Author: Pravin Shanmugavel
Project: ExpenseIQ

Creating an expense requires authentication - the claim is always
submitted as the logged-in employee (employee_id in the body is
ignored/overridden).
"""

from uuid import uuid4

from tests.helpers import create_employee, create_project

EXPENSE_URL = "/api/v1/expenses"


def create_expense_payload(client, hr_head_headers):

    unique = uuid4().hex[:6]

    requester, requester_headers = create_employee(client, hr_head_headers)
    project_id = create_project(client, hr_head_headers)

    payload = {
        "expense_number": f"EXP{unique}",
        "employee_id": requester["id"],
        "project_id": project_id,
        "expense_category": "Travel",
        "merchant_name": "Uber",
        "amount": 450.75,
        "currency": "INR",
        "expense_date": "2026-07-14",
        "payment_method": "Credit Card",
        "description": "Travel to client office",
    }

    return payload, requester_headers


def test_create_expense_requires_authentication(client, hr_head_headers):

    payload, _ = create_expense_payload(client, hr_head_headers)

    response = client.post(f"{EXPENSE_URL}/", json=payload)

    assert response.status_code == 401


def test_create_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    response = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert response.status_code == 201

    data = response.json()

    assert data["expense_number"] == payload["expense_number"]
    assert data["merchant_name"] == payload["merchant_name"]
    assert data["employee_id"] == payload["employee_id"]
    assert "id" in data


def test_create_expense_ignores_forged_employee_id(client, hr_head_headers):
    """
    Even if the body names a different employee_id, the server must
    submit the claim as whoever is actually authenticated.
    """

    payload, headers = create_expense_payload(client, hr_head_headers)

    forged_requester, _ = create_employee(client, hr_head_headers)
    payload["employee_id"] = forged_requester["id"]

    response = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert response.status_code == 201
    assert response.json()["employee_id"] != forged_requester["id"]


def test_get_all_expenses(client):

    response = client.get(f"{EXPENSE_URL}/")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_expense_by_id(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.get(f"{EXPENSE_URL}/{expense_id}")

    assert response.status_code == 200
    assert response.json()["id"] == expense_id


def test_update_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.put(
        f"{EXPENSE_URL}/{expense_id}",
        json={"merchant_name": "Ola Cabs"},
    )

    assert response.status_code == 200
    assert response.json()["merchant_name"] == "Ola Cabs"


def test_delete_expense(client, hr_head_headers):

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    response = client.delete(f"{EXPENSE_URL}/{expense_id}")

    assert response.status_code == 204


def test_delete_expense_cascades_ai_pipeline_child_rows(
    client,
    hr_head_headers,
):
    """
    Regression test for a real bug: deleting an expense that has gone
    through the AI pipeline (receipt + duplicate check + compliance
    check + AI analysis, each with a NOT NULL expense_id) used to fail
    with an IntegrityError, because those relationships on the Expense
    model had no delete cascade - SQLAlchemy tried to null out the FK
    instead of deleting the child rows. Covers all 4 child tables at
    once, matching what the real pipeline actually creates per
    receipt upload.
    """

    from app.database.session import SessionLocal
    from app.models.ai_review import AIAnalysis
    from app.models.compliance_check import ComplianceCheck
    from app.models.duplicate_check import DuplicateCheck
    from app.models.receipt import Receipt

    payload, headers = create_expense_payload(client, hr_head_headers)

    create = client.post(f"{EXPENSE_URL}/", json=payload, headers=headers)

    assert create.status_code == 201

    expense_id = create.json()["id"]

    db = SessionLocal()

    try:
        receipt = Receipt(
            receipt_number=f"RCT{uuid4().hex[:8]}",
            expense_id=expense_id,
            original_filename="test.jpg",
            stored_filename="test.jpg",
            file_path="uploads/receipts/test.jpg",
            file_type="image/jpeg",
            file_size=100,
        )
        db.add(receipt)
        db.commit()
        db.refresh(receipt)

        db.add(
            DuplicateCheck(
                expense_id=expense_id,
                duplicate_found=False,
                confidence_score=0,
            )
        )
        db.add(
            ComplianceCheck(
                expense_id=expense_id,
                policy_status="PASS",
            )
        )
        db.add(
            AIAnalysis(
                expense_id=expense_id,
                receipt_id=receipt.id,
                policy_status="PASS",
                requires_manager_approval=False,
                approval_recommendation="AUTO_APPROVE_RECOMMENDED",
                ai_provider="gemini",
                ocr_provider="Tesseract",
                policy_provider="Groq",
                pipeline_version="2.0.0",
            )
        )
        db.commit()
    finally:
        db.close()

    response = client.delete(f"{EXPENSE_URL}/{expense_id}")

    assert response.status_code == 204

    db = SessionLocal()

    try:
        assert (
            db.query(Receipt)
            .filter(Receipt.expense_id == expense_id)
            .count()
            == 0
        )
        assert (
            db.query(DuplicateCheck)
            .filter(DuplicateCheck.expense_id == expense_id)
            .count()
            == 0
        )
        assert (
            db.query(ComplianceCheck)
            .filter(ComplianceCheck.expense_id == expense_id)
            .count()
            == 0
        )
        assert (
            db.query(AIAnalysis)
            .filter(AIAnalysis.expense_id == expense_id)
            .count()
            == 0
        )
    finally:
        db.close()
