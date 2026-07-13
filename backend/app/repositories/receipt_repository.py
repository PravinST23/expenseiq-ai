"""
Receipt Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.repositories.base_repository import BaseRepository


class ReceiptRepository(BaseRepository[Receipt]):
    """
    Repository for Receipt operations.
    """

    def __init__(self):
        super().__init__(Receipt)

    def get_by_receipt_number(
        self,
        db: Session,
        receipt_number: str,
    ):
        return (
            db.query(Receipt)
            .filter(
                Receipt.receipt_number == receipt_number
            )
            .first()
        )

    def get_by_id(
        self,
        db: Session,
        receipt_id: UUID,
    ):
        return (
            db.query(Receipt)
            .filter(
                Receipt.id == receipt_id
            )
            .first()
        )

    def update(
        self,
        db: Session,
        receipt: Receipt,
    ):
        db.commit()
        db.refresh(receipt)
        return receipt

    def delete(
        self,
        db: Session,
        receipt: Receipt,
    ):
        db.delete(receipt)
        db.commit()


receipt_repository = ReceiptRepository()