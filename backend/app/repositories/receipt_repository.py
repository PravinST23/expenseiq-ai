"""
Receipt Repository

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.repositories.base_repository import BaseRepository


class ReceiptRepository(BaseRepository[Receipt]):
    """
    Repository for Receipt operations.
    """

    def __init__(self):
        super().__init__(Receipt)

    def get_by_expense_id(
        self,
        db: Session,
        expense_id,
    ):
        return (
            db.query(Receipt)
            .filter(Receipt.expense_id == expense_id)
            .first()
        )


receipt_repository = ReceiptRepository()