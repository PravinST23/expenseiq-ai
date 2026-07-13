"""
Receipt Service

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session

from app.models.receipt import Receipt
from app.repositories.receipt_repository import receipt_repository
from app.schemas.receipt import ReceiptCreate
from app.schemas.receipt import ReceiptUpdate


class ReceiptService:
    """
    Business logic for Receipt operations.
    """

    def create_receipt(
        self,
        db: Session,
        receipt: ReceiptCreate,
    ):
        """
        Create a new receipt.
        """

        existing = receipt_repository.get_by_receipt_number(
            db,
            receipt.receipt_number,
        )

        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Receipt Number already exists.",
            )

        new_receipt = Receipt(
            **receipt.model_dump()
        )

        return receipt_repository.create(
            db,
            new_receipt,
        )

    def upload_receipt(
        self,
        db: Session,
        receipt: ReceiptCreate,
    ):
        """
        Save uploaded receipt metadata into the database.
        """

        return self.create_receipt(
            db,
            receipt,
        )

    def get_all(
        self,
        db: Session,
    ):
        """
        Get all receipts.
        """

        return receipt_repository.get_all(db)

    def get_by_id(
        self,
        db: Session,
        receipt_id: UUID,
    ):
        """
        Get receipt by ID.
        """

        receipt = receipt_repository.get_by_id(
            db,
            receipt_id,
        )

        if receipt is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Receipt not found.",
            )

        return receipt

    def update_receipt(
        self,
        db: Session,
        receipt_id: UUID,
        receipt_update: ReceiptUpdate,
    ):
        """
        Update receipt details.
        """

        receipt = self.get_by_id(
            db,
            receipt_id,
        )

        update_data = receipt_update.model_dump(
            exclude_unset=True,
        )

        for key, value in update_data.items():
            setattr(
                receipt,
                key,
                value,
            )

        return receipt_repository.update(
            db,
            receipt,
        )

    def delete_receipt(
        self,
        db: Session,
        receipt_id: UUID,
    ):
        """
        Delete a receipt.
        """

        receipt = self.get_by_id(
            db,
            receipt_id,
        )

        receipt_repository.delete(
            db,
            receipt,
        )


receipt_service = ReceiptService()