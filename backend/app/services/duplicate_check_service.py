"""
Duplicate Check Service

Author: Pravin Shanmugavel
Project: ExpenseIQ

Implements Novelty 2 - Duplicate Expense Fraud Detection.

Runs a multi-field duplicate check for a submitted expense against
every other expense in the system (including across employees, to
catch duplicate invoice numbers submitted by different people):

  - merchant name  -> fuzzy match via Python difflib
  - amount         -> exact / near-exact match
  - expense date   -> exact match
  - invoice number -> exact match (from AI-extracted receipt data)

Any 3 of these 4 fields matching marks the claim as a duplicate,
per the approved proposal ("any three fields trigger DUPLICATE
DETECTED").
"""

import json
from difflib import SequenceMatcher
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.duplicate_check import DuplicateCheck
from app.models.expense import Expense
from app.models.ai_review import AIAnalysis
from app.repositories.duplicate_check_repository import (
    duplicate_check_repository,
)
from app.schemas.duplicate_check import DuplicateCheckCreate

MERCHANT_SIMILARITY_THRESHOLD = 0.85
AMOUNT_TOLERANCE = Decimal("1.00")
MATCH_FIELDS_REQUIRED = 3


def _merchant_similarity(a: str | None, b: str | None) -> float:

    if not a or not b:
        return 0.0

    return SequenceMatcher(
        None,
        a.strip().lower(),
        b.strip().lower(),
    ).ratio()


def _invoice_number(db: Session, expense_id) -> str | None:
    """
    Pulls the AI-extracted invoice number for an expense, if any.
    """

    analysis = (
        db.query(AIAnalysis)
        .filter(AIAnalysis.expense_id == expense_id)
        .order_by(AIAnalysis.processed_at.desc())
        .first()
    )

    if analysis is None or not analysis.extracted_json:
        return None

    try:
        data = json.loads(analysis.extracted_json)
    except (json.JSONDecodeError, TypeError):
        return None

    invoice_number = data.get("invoice_number")

    if not invoice_number:
        return None

    return str(invoice_number).strip().lower()


class DuplicateCheckService:

    def create(
        self,
        db: Session,
        duplicate: DuplicateCheckCreate,
    ):

        new_record = DuplicateCheck(
            **duplicate.model_dump()
        )

        return duplicate_check_repository.create(
            db,
            new_record,
        )

    def run_check(
        self,
        db: Session,
        expense: Expense,
    ) -> DuplicateCheck:
        """
        Run the multi-field duplicate check for an expense and
        persist (create or update) the result.
        """

        candidates = (
            db.query(Expense)
            .filter(Expense.id != expense.id)
            .all()
        )

        this_invoice = _invoice_number(db, expense.id)

        best_match = None
        best_score = 0
        best_fields: list[str] = []

        for candidate in candidates:

            matched_fields = []

            if (
                _merchant_similarity(
                    expense.merchant_name,
                    candidate.merchant_name,
                )
                >= MERCHANT_SIMILARITY_THRESHOLD
            ):
                matched_fields.append("merchant_name")

            if (
                candidate.amount is not None
                and expense.amount is not None
                and abs(candidate.amount - expense.amount)
                <= AMOUNT_TOLERANCE
            ):
                matched_fields.append("amount")

            if (
                candidate.expense_date == expense.expense_date
            ):
                matched_fields.append("expense_date")

            candidate_invoice = _invoice_number(db, candidate.id)

            if (
                this_invoice
                and candidate_invoice
                and this_invoice == candidate_invoice
            ):
                matched_fields.append("invoice_number")

            if len(matched_fields) > best_score:
                best_score = len(matched_fields)
                best_match = candidate
                best_fields = matched_fields

        duplicate_found = best_score >= MATCH_FIELDS_REQUIRED

        confidence_score = Decimal(
            str(round((best_score / 4) * 100, 2))
        )

        existing = duplicate_check_repository.get_by_expense_id(
            db,
            expense.id,
        )

        if existing:

            existing.duplicate_found = duplicate_found
            existing.confidence_score = confidence_score
            existing.matched_expense_id = (
                best_match.id if best_match else None
            )
            existing.match_fields = (
                ",".join(best_fields) if best_fields else None
            )

            return duplicate_check_repository.update(
                db,
                existing,
            )

        new_record = DuplicateCheck(
            expense_id=expense.id,
            duplicate_found=duplicate_found,
            confidence_score=confidence_score,
            matched_expense_id=(
                best_match.id if best_match else None
            ),
            match_fields=(
                ",".join(best_fields) if best_fields else None
            ),
        )

        return duplicate_check_repository.create(
            db,
            new_record,
        )

    def get_all(self, db: Session):
        return duplicate_check_repository.get_all(db)

    def get_by_expense(self, db: Session, expense_id):
        return duplicate_check_repository.get_by_expense_id(
            db,
            expense_id,
        )


duplicate_check_service = DuplicateCheckService()
