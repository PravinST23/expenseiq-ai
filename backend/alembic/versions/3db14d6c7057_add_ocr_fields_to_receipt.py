"""Add OCR fields to Receipt

Revision ID: 3db14d6c7057
Revises: e2cec6f419ec
Create Date: 2026-07-14 12:09:13.360355
"""

from typing import Sequence
from typing import Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3db14d6c7057"
down_revision: Union[str, Sequence[str], None] = "e2cec6f419ec"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Upgrade schema.
    """

    op.add_column(
        "receipts",
        sa.Column(
            "ocr_text",
            sa.Text(),
            nullable=True,
        ),
    )

    op.add_column(
        "receipts",
        sa.Column(
            "ocr_status",
            sa.String(20),
            nullable=False,
            server_default="Pending",
        ),
    )

    op.add_column(
        "receipts",
        sa.Column(
            "ocr_processed_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.add_column(
        "receipts",
        sa.Column(
            "ai_status",
            sa.String(20),
            nullable=False,
            server_default="Pending",
        ),
    )

    op.add_column(
        "receipts",
        sa.Column(
            "extracted_json",
            sa.Text(),
            nullable=True,
        ),
    )

    # Remove defaults after existing rows are updated
    op.alter_column(
        "receipts",
        "ocr_status",
        server_default=None,
    )

    op.alter_column(
        "receipts",
        "ai_status",
        server_default=None,
    )


def downgrade() -> None:
    """
    Downgrade schema.
    """

    op.drop_column(
        "receipts",
        "extracted_json",
    )

    op.drop_column(
        "receipts",
        "ai_status",
    )

    op.drop_column(
        "receipts",
        "ocr_processed_at",
    )

    op.drop_column(
        "receipts",
        "ocr_status",
    )

    op.drop_column(
        "receipts",
        "ocr_text",
    )