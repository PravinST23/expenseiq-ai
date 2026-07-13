"""
Receipt Service
"""

from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.repositories.receipt_repository import receipt_repository
from app.schemas.receipt import ReceiptCreate


class ReceiptService:

    def create_receipt(
        self,
        db: Session,
        receipt: ReceiptCreate,
    ):

        new_receipt = Receipt(
            **receipt.model_dump()
        )

        return receipt_repository.create(
            db,
            new_receipt,
        )


receipt_service = ReceiptService()