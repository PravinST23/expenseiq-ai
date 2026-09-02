"""
Analytics API

Author: Pravin Shanmugavel
Project: ExpenseIQ

JSON data-feed endpoints consumed by:
  - the React manager dashboard (charts / KPI tiles)
  - Power BI Desktop, via Get Data -> Web -> this endpoint's URL

Covers the RFP's required Power BI views: spend by category, spend
by employee, spend by project, approval status summary, and the
reimbursement liability tracker - plus an AI accuracy feed used for
QA evidence (risk score distribution, auto-approval mix, duplicate
rate).
"""

from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy import case
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.models.compliance_check import ComplianceCheck
from app.models.employee import Employee
from app.models.expense import Expense
from app.models.project import Project
from app.models.receipt import Receipt

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get(
    "/spend-by-category",
    summary="Total Spend By Expense Category",
)
def spend_by_category(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Expense.expense_category.label("category"),
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count"),
        )
        .group_by(Expense.expense_category)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    return [
        {
            "category": r.category,
            "total_amount": float(r.total_amount or 0),
            "count": r.count,
        }
        for r in rows
    ]


@router.get(
    "/spend-by-employee",
    summary="Total Spend By Employee",
)
def spend_by_employee(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Employee.id.label("employee_id"),
            Employee.full_name.label("employee_name"),
            Employee.department.label("department"),
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count"),
        )
        .join(Expense, Expense.employee_id == Employee.id)
        .group_by(Employee.id, Employee.full_name, Employee.department)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    return [
        {
            "employee_id": str(r.employee_id),
            "employee_name": r.employee_name,
            "department": r.department,
            "total_amount": float(r.total_amount or 0),
            "count": r.count,
        }
        for r in rows
    ]


@router.get(
    "/spend-by-project",
    summary="Total Spend By Project",
)
def spend_by_project(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Project.id.label("project_id"),
            Project.project_name.label("project_name"),
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count"),
        )
        .join(Expense, Expense.project_id == Project.id)
        .group_by(Project.id, Project.project_name)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    return [
        {
            "project_id": str(r.project_id),
            "project_name": r.project_name,
            "total_amount": float(r.total_amount or 0),
            "count": r.count,
        }
        for r in rows
    ]


@router.get(
    "/approval-status-summary",
    summary="Approval Status Summary",
)
def approval_status_summary(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Expense.status.label("status"),
            func.count(Expense.id).label("count"),
        )
        .group_by(Expense.status)
        .all()
    )

    return [
        {"status": r.status, "count": r.count} for r in rows
    ]


@router.get(
    "/reimbursement-liability",
    summary="Reimbursement Liability Tracker",
)
def reimbursement_liability(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Expense.reimbursement_state.label("state"),
            func.sum(Expense.amount).label("total_amount"),
            func.count(Expense.id).label("count"),
        )
        .group_by(Expense.reimbursement_state)
        .all()
    )

    by_state = [
        {
            "state": r.state,
            "total_amount": float(r.total_amount or 0),
            "count": r.count,
        }
        for r in rows
    ]

    outstanding = sum(
        item["total_amount"]
        for item in by_state
        if item["state"] in ("PENDING", "APPROVED")
    )

    return {
        "by_state": by_state,
        "outstanding_liability": outstanding,
    }


@router.get(
    "/ai-accuracy",
    summary="AI Pipeline Accuracy / Risk Feed",
)
def ai_accuracy(db: Session = Depends(get_db)):

    total = db.query(func.count(Expense.id)).scalar() or 0

    duplicates = (
        db.query(func.count(Expense.id))
        .filter(Expense.is_duplicate.is_(True))
        .scalar()
        or 0
    )

    avg_fraud = (
        db.query(func.avg(Expense.fraud_risk_score)).scalar()
    )
    avg_compliance = (
        db.query(func.avg(Expense.compliance_risk_score)).scalar()
    )
    avg_confidence = (
        db.query(func.avg(Expense.ai_confidence_score)).scalar()
    )

    recommendation_rows = (
        db.query(
            Expense.ai_recommendation.label("recommendation"),
            func.count(Expense.id).label("count"),
        )
        .filter(Expense.ai_recommendation.isnot(None))
        .group_by(Expense.ai_recommendation)
        .all()
    )

    engine_rows = (
        db.query(
            Expense.processing_engine.label("engine"),
            func.count(Expense.id).label("count"),
        )
        .filter(Expense.processing_engine.isnot(None))
        .group_by(Expense.processing_engine)
        .all()
    )

    return {
        "total_expenses": total,
        "duplicate_count": duplicates,
        "duplicate_rate": (
            round((duplicates / total) * 100, 2) if total else 0
        ),
        "average_fraud_risk": (
            float(avg_fraud) if avg_fraud is not None else None
        ),
        "average_compliance_risk": (
            float(avg_compliance)
            if avg_compliance is not None
            else None
        ),
        "average_confidence": (
            float(avg_confidence)
            if avg_confidence is not None
            else None
        ),
        "recommendation_mix": [
            {"recommendation": r.recommendation, "count": r.count}
            for r in recommendation_rows
        ],
        "processing_engine_mix": [
            {"engine": r.engine, "count": r.count}
            for r in engine_rows
        ],
    }


@router.get(
    "/overview",
    summary="Executive Overview KPIs",
)
def overview(db: Session = Depends(get_db)):

    total_employees = db.query(func.count(Employee.id)).scalar() or 0
    total_expenses = db.query(func.count(Expense.id)).scalar() or 0
    total_amount = db.query(func.sum(Expense.amount)).scalar() or 0

    approved_amount = (
        db.query(func.sum(Expense.amount))
        .filter(Expense.status == "Approved")
        .scalar()
        or 0
    )

    pending_count = (
        db.query(func.count(Expense.id))
        .filter(Expense.status.like("Pending%"))
        .scalar()
        or 0
    )

    rejected_count = (
        db.query(func.count(Expense.id))
        .filter(Expense.status == "Rejected")
        .scalar()
        or 0
    )

    return {
        "total_employees": total_employees,
        "total_expenses": total_expenses,
        "total_amount": float(total_amount),
        "approved_amount": float(approved_amount),
        "pending_count": pending_count,
        "rejected_count": rejected_count,
    }


@router.get(
    "/department-status-summary",
    summary="Department-wise Expense Status Breakdown (Approved / Pending / Rejected)",
)
def department_status_summary(db: Session = Depends(get_db)):

    status_bucket = case(
        (Expense.status == "Approved", "Approved"),
        (Expense.status == "Rejected", "Rejected"),
        else_="Pending",
    ).label("status_bucket")

    rows = (
        db.query(
            Employee.department.label("department"),
            status_bucket,
            func.count(Expense.id).label("count"),
        )
        .join(Employee, Expense.employee_id == Employee.id)
        .group_by(Employee.department, status_bucket)
        .all()
    )

    return [
        {
            "department": r.department,
            "status_bucket": r.status_bucket,
            "count": r.count,
        }
        for r in rows
    ]


@router.get(
    "/expense-detail",
    summary="Expense Detail Table (employee / project / category / amount / status)",
)
def expense_detail(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Employee.full_name.label("employee_name"),
            Project.project_name.label("project_name"),
            Expense.expense_category.label("expense_category"),
            Expense.amount.label("amount"),
            Expense.currency.label("currency"),
            Expense.status.label("status"),
            Expense.expense_date.label("expense_date"),
        )
        .join(Employee, Expense.employee_id == Employee.id)
        .join(Project, Expense.project_id == Project.id)
        .order_by(Expense.created_at.desc())
        .all()
    )

    return [
        {
            "employee_name": r.employee_name,
            "project_name": r.project_name,
            "expense_category": r.expense_category,
            "amount": float(r.amount),
            "currency": r.currency,
            "status": r.status,
            "expense_date": str(r.expense_date),
        }
        for r in rows
    ]


@router.get(
    "/receipt-ai-detail",
    summary="Receipt AI Detail Table (receipt / merchant / amount / engine / policy / recommendation)",
)
def receipt_ai_detail(db: Session = Depends(get_db)):

    rows = (
        db.query(
            Receipt.receipt_number.label("receipt_number"),
            Expense.merchant_name.label("merchant_name"),
            Expense.amount.label("amount"),
            Expense.currency.label("currency"),
            Expense.processing_engine.label("processing_engine"),
            ComplianceCheck.policy_status.label("policy_status"),
            Expense.ai_recommendation.label("ai_recommendation"),
        )
        .join(Expense, Receipt.expense_id == Expense.id)
        .outerjoin(ComplianceCheck, ComplianceCheck.expense_id == Expense.id)
        .order_by(Receipt.created_at.desc())
        .all()
    )

    return [
        {
            "receipt_number": r.receipt_number,
            "merchant_name": r.merchant_name,
            "amount": float(r.amount),
            "currency": r.currency,
            "processing_engine": r.processing_engine,
            "policy_status": r.policy_status,
            "ai_recommendation": r.ai_recommendation,
        }
        for r in rows
    ]
