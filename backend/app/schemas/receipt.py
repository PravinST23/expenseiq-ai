"""
Receipt Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class ReceiptBase(BaseModel):
    """
    Common Receipt Fields.
    """

    receipt_number: str = Field(
        ...,
        examples=["RCT001"],
    )

    expense_id: UUID

    original_filename: str

    stored_filename: str

    file_path: str

    file_type: str

    file_size: int


class ReceiptCreate(ReceiptBase):
    """
    Request schema for creating a receipt.
    """
    pass


class ReceiptUpdate(BaseModel):
    """
    Request schema for updating a receipt.
    """

    original_filename: str | None = None

    stored_filename: str | None = None

    file_path: str | None = None

    file_type: str | None = None

    file_size: int | None = None

    upload_status: str | None = None

    # OCR Fields

    ocr_text: str | None = None

    ocr_status: str | None = None

    ocr_processed_at: datetime | None = None

    # AI Fields

    ai_status: str | None = None

    extracted_json: str | None = None


class ReceiptResponse(ReceiptBase):
    """
    Response schema.
    """

    id: UUID

    upload_status: str

    # OCR Fields

    ocr_text: str | None

    ocr_status: str

    ocr_processed_at: datetime | None

    # AI Fields

    ai_status: str

    extracted_json: str | None

    model_config = ConfigDict(
        from_attributes=True
    )