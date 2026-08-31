"""
Wipe Data

Author: Pravin Shanmugavel
Project: ExpenseIQ

Truncates every application data table (schema untouched) so the
database starts clean - no demo/test employees, expenses, receipts,
approvals, or AI analysis records. Run this once, then
scripts/bootstrap_org.py to set up the real MAC teams/projects, then
add real employees via POST /auth/signup or POST /employees/ (HR_HEAD)
exactly as a live deployment would.

    python scripts/wipe_data.py --yes
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text  # noqa: E402

from app.database.session import engine  # noqa: E402

# Order doesn't matter - TRUNCATE ... CASCADE handles FK dependencies.
TABLES = [
    "expense_ai_analysis",
    "compliance_checks",
    "duplicate_checks",
    "expense_approvals",
    "receipts",
    "expenses",
    "projects",
    "employees",
    "teams",
]


def main():

    if "--yes" not in sys.argv:
        print(
            "This permanently deletes ALL rows from: "
            f"{', '.join(TABLES)}.\n"
            "Re-run with --yes to confirm."
        )
        return

    with engine.begin() as conn:

        conn.execute(
            text(f"TRUNCATE TABLE {', '.join(TABLES)} CASCADE")
        )

    print(f"Wiped {len(TABLES)} tables:")
    for table in TABLES:
        print(f"  - {table}")


if __name__ == "__main__":
    main()
