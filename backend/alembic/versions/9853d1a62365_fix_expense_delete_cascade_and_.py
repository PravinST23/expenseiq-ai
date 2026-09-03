"""fix expense delete cascade and duplicate check matched expense ondelete

Revision ID: 9853d1a62365
Revises: 2b130a503ec9
Create Date: 2026-09-03 11:45:48.603920

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9853d1a62365'
down_revision: Union[str, Sequence[str], None] = '2b130a503ec9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema.

    duplicate_checks.matched_expense_id is a nullable "this expense was
    flagged as a duplicate of that one" pointer, with no ondelete
    behavior at the DB level - deleting the *matched* expense while
    another expense's duplicate_check row still points to it via
    matched_expense_id would raise a plain foreign-key violation.
    Since the column is nullable, SET NULL is the correct behavior:
    the match reference just clears, it doesn't block deletion.

    (duplicate_checks.expense_id / compliance_checks.expense_id /
    expense_ai_analysis.expense_id are NOT NULL and are fixed instead
    via ORM-level cascade="all, delete-orphan" on the Expense model's
    relationships, matching receipts/approvals - no DB constraint
    change needed for those.)
    """
    op.drop_constraint(
        "duplicate_checks_matched_expense_id_fkey",
        "duplicate_checks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "duplicate_checks_matched_expense_id_fkey",
        "duplicate_checks",
        "expenses",
        ["matched_expense_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "duplicate_checks_matched_expense_id_fkey",
        "duplicate_checks",
        type_="foreignkey",
    )
    op.create_foreign_key(
        "duplicate_checks_matched_expense_id_fkey",
        "duplicate_checks",
        "expenses",
        ["matched_expense_id"],
        ["id"],
    )
