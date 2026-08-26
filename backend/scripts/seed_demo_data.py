"""
Demo Data Seeder

Author: Pravin Shanmugavel
Project: ExpenseIQ

Generates the RFP's minimum-coverage evidence set in one run:
  - 6 employees across 4 departments, each with a login-ready
    password (see DEMO_PASSWORD below) and an approval role
    (EMPLOYEE / L1_MANAGER / L2_FINANCE / L3_CFO)
  - 3 projects
  - 1 expense per existing receipt image in uploads/receipts/
    (>= 20 receipts, spread across 5 categories) run through the
    FULL AI pipeline: OCR -> Hybrid Router (Gemini/Ollama) ->
    Duplicate Detector -> Groq risk scoring -> Auto-Approval Engine
  - a mix of is_sensitive claims routed through Ollama offline
  - approval actions walking claims through L1/L2/L3 as required,
    each recorded under the real approver Employee's identity
    (exactly as the authenticated HTTP API would do it)
  - reimbursement state transitions across PENDING/APPROVED/PAID

Run from backend/ with the virtualenv active:

    python scripts/seed_demo_data.py

All seeded accounts share one demo password (see DEMO_PASSWORD) -
log in via POST /api/v1/auth/login with any seeded employee's email.
"""

import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.session import SessionLocal  # noqa: E402
from app.schemas.employee import EmployeeCreate  # noqa: E402
from app.schemas.project import ProjectCreate  # noqa: E402
from app.schemas.expense import ExpenseCreate  # noqa: E402
from app.schemas.receipt import ReceiptCreate  # noqa: E402
from app.schemas.approval import ApprovalCreate  # noqa: E402
from app.schemas.expense import ReimbursementUpdate  # noqa: E402
from app.services.employee_service import employee_service  # noqa: E402
from app.services.project_service import project_service  # noqa: E402
from app.services.expense_service import expense_service  # noqa: E402
from app.services.receipt_service import receipt_service  # noqa: E402
from app.services.approval_service import approval_service  # noqa: E402

RECEIPTS_DIR = Path(__file__).resolve().parent.parent / "uploads" / "receipts"

CATEGORIES = [
    "Travel",
    "Meals",
    "Hotel",
    "Office Supplies",
    "Entertainment",
]

MERCHANTS = [
    "Uber", "Marriott Hotels", "Cafe Coffee Day", "Staples",
    "The Leela Palace", "IndiGo Airlines", "Ola Cabs", "Domino's Pizza",
    "WeWork", "Amazon Business", "Radisson Blu", "Taj Hotels",
    "Zomato", "Swiggy", "MakeMyTrip", "Reliance Digital",
]

PAYMENT_METHODS = ["Card", "UPI", "Cash", "Bank Transfer"]

# Shared demo password for every seeded account - this is throwaway
# local/demo data, never production credentials.
DEMO_PASSWORD = "Demo@12345"

EMPLOYEES = [
    dict(employee_code="EMP001", full_name="Ananya Sharma", email="ananya.sharma@psiog.demo", department="Engineering", designation="Senior Engineer", role="EMPLOYEE"),
    dict(employee_code="EMP002", full_name="Rohan Verma", email="rohan.verma@psiog.demo", department="Sales", designation="Account Executive", role="EMPLOYEE"),
    dict(employee_code="EMP003", full_name="Priya Nair", email="priya.nair@psiog.demo", department="Marketing", designation="Marketing Lead", role="EMPLOYEE"),
    dict(employee_code="EMP004", full_name="Karthik Iyer", email="karthik.iyer@psiog.demo", department="Engineering", designation="Engineering Manager", role="L1_MANAGER"),
    dict(employee_code="EMP005", full_name="Fatima Khan", email="fatima.khan@psiog.demo", department="Finance", designation="Finance Analyst", role="L2_FINANCE"),
    dict(employee_code="EMP006", full_name="Meera Krishnan", email="meera.krishnan@psiog.demo", department="Finance", designation="Chief Financial Officer", role="L3_CFO"),
]

PROJECTS = [
    dict(project_code="PRJ-ALPHA", project_name="Project Alpha", client_name="Internal", project_manager="Karthik Iyer", project_budget=500000),
    dict(project_code="PRJ-BETA", project_name="Project Beta", client_name="Acme Corp", project_manager="Priya Nair", project_budget=750000),
    dict(project_code="PRJ-GAMMA", project_name="Project Gamma", client_name="Globex Inc", project_manager="Rohan Verma", project_budget=300000),
]


def get_or_create_employees(db):
    from app.repositories.employee_repository import employee_repository
    from app.schemas.employee import EmployeeUpdate

    by_role = {}
    ids = []
    for payload in EMPLOYEES:
        payload = {**payload, "password": DEMO_PASSWORD}
        try:
            emp = employee_service.create_employee(db, EmployeeCreate(**payload))
        except Exception:
            db.rollback()
            emp = employee_repository.get_by_employee_code(db, payload["employee_code"])

            # Retrofit accounts seeded before login existed (role
            # defaulted to EMPLOYEE, no password) so re-running this
            # script always leaves every seeded account login-ready.
            if emp is not None and (
                not emp.has_password or emp.role != payload["role"]
            ):
                emp = employee_service.update_employee(
                    db,
                    emp.id,
                    EmployeeUpdate(
                        role=payload["role"],
                        password=DEMO_PASSWORD,
                    ),
                )

        ids.append(emp.id)
        by_role.setdefault(emp.role, emp)
    return ids, by_role


def get_or_create_projects(db):
    ids = []
    for payload in PROJECTS:
        try:
            proj = project_service.create_project(db, ProjectCreate(**payload))
        except Exception:
            db.rollback()
            from app.repositories.project_repository import project_repository
            proj = project_repository.get_by_project_code(db, payload["project_code"])
        ids.append(proj.id)
    return ids


def main():
    db = SessionLocal()

    receipts = sorted(RECEIPTS_DIR.glob("*.jpg"))

    if len(receipts) < 20:
        print(
            f"WARNING: only {len(receipts)} receipt images found in "
            f"{RECEIPTS_DIR} - RFP minimum is 20."
        )

    print(f"Found {len(receipts)} receipt images to process.\n")

    employee_ids, approvers_by_role = get_or_create_employees(db)
    project_ids = get_or_create_projects(db)

    print(
        f"Seeded {len(employee_ids)} employees, {len(project_ids)} "
        f"projects. Demo login password for all: {DEMO_PASSWORD!r}\n"
    )

    created_expense_ids = []

    for index, receipt_path in enumerate(receipts):

        category = CATEGORIES[index % len(CATEGORIES)]
        employee_id = employee_ids[index % len(employee_ids)]
        project_id = project_ids[index % len(project_ids)]
        merchant = MERCHANTS[index % len(MERCHANTS)]
        amount = round(random.uniform(200, 9500), 2)
        is_sensitive = index < 6  # first 6 -> Ollama offline path (>=5 required)

        expense = expense_service.create_expense(
            db,
            ExpenseCreate(
                expense_number=f"EXP-DEMO-{index + 1:03d}",
                employee_id=employee_id,
                project_id=project_id,
                expense_category=category,
                merchant_name=merchant,
                amount=amount,
                currency="INR",
                expense_date="2026-08-01",
                payment_method=PAYMENT_METHODS[index % len(PAYMENT_METHODS)],
                description=f"Demo seed expense #{index + 1}",
                is_sensitive=is_sensitive,
            ),
        )

        created_expense_ids.append(expense.id)

        engine = "Ollama (offline)" if is_sensitive else "Gemini (cloud)"
        print(
            f"[{index + 1}/{len(receipts)}] {expense.expense_number} "
            f"({category}, {engine}) - uploading {receipt_path.name} ..."
        )

        receipt_schema = ReceiptCreate(
            receipt_number=f"RCT-DEMO-{index + 1:03d}",
            expense_id=expense.id,
            original_filename=receipt_path.name,
            stored_filename=receipt_path.name,
            file_path=str(receipt_path),
            file_type="image/jpeg",
            file_size=receipt_path.stat().st_size,
        )

        try:
            receipt_service.upload_receipt(db, receipt_schema)
        except Exception as ex:
            print(f"    ! pipeline error: {ex}")

        db.refresh(expense)
        print(
            f"    -> status={expense.status} "
            f"recommendation={expense.ai_recommendation} "
            f"engine={expense.processing_engine} "
            f"duplicate={expense.is_duplicate}"
        )

        # Be polite to the Gemini / Groq free tiers.
        time.sleep(4)

    # -------------------------------------------------------
    # Walk a subset of claims through the approval workflow so
    # reimbursement states are populated across all 3 stages.
    # -------------------------------------------------------

    print("\nRunning approval actions on pending claims...\n")

    from app.models.expense import Expense

    pending = (
        db.query(Expense)
        .filter(Expense.id.in_(created_expense_ids))
        .filter(Expense.status.like("Pending%"))
        .all()
    )

    for i, expense in enumerate(pending):

        # Reject roughly 1 in 6 to demonstrate the terminal path too.
        reject = i % 6 == 5

        for level in range(1, expense.required_approval_level + 1):

            role = {1: "L1_MANAGER", 2: "L2_FINANCE", 3: "L3_CFO"}[level]
            approver = approvers_by_role[role]

            action = "Rejected" if (reject and level == expense.required_approval_level) else "Approved"

            try:
                # current_employee mirrors exactly what the
                # authenticated HTTP API does - the approver's real
                # identity, not a client-supplied role/name.
                approval_service.create_approval(
                    db,
                    ApprovalCreate(
                        expense_id=expense.id,
                        action=action,
                        comments=f"Demo seed {action.lower()} at {role}",
                    ),
                    current_employee=approver,
                )
            except Exception as ex:
                print(f"    ! approval error on {expense.expense_number}: {ex}")
                break

            if action == "Rejected":
                break

    # -------------------------------------------------------
    # Mark a portion of the now-Approved claims as PAID.
    # -------------------------------------------------------

    approved = (
        db.query(Expense)
        .filter(Expense.id.in_(created_expense_ids))
        .filter(Expense.status == "Approved")
        .all()
    )

    print(f"\n{len(approved)} claims fully approved. Marking half as PAID...\n")

    finance_approver = approvers_by_role["L2_FINANCE"]

    for i, expense in enumerate(approved):
        if i % 2 == 0:
            expense_service.update_reimbursement(
                db,
                expense.id,
                ReimbursementUpdate(reimbursement_state="PAID"),
                current_employee=finance_approver,
            )

    db.close()

    print("\nSeeding complete.")
    print(f"  Expenses created: {len(created_expense_ids)}")
    print(f"  Approved: {len(approved)}")


if __name__ == "__main__":
    main()
