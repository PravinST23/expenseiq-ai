"""
Receipt Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

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
    pass


class ReceiptUpdate(BaseModel):

    original_filename: str | None = None

    stored_filename: str | None = None

    file_path: str | None = None

    file_type: str | None = None

    file_size: int | None = None

    upload_status: str | None = None


class ReceiptResponse(ReceiptBase):

    id: UUID

    upload_status: str

    model_config = ConfigDict(
        from_attributes=True
    )