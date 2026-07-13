"""
Receipt Schemas

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ReceiptBase(BaseModel):

    expense_id: UUID
    original_file_name: str
    stored_file_name: str
    file_path: str
    file_type: str


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptResponse(ReceiptBase):

    id: UUID

    model_config = ConfigDict(
        from_attributes=True
    )