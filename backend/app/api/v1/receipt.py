"""
Receipt API

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from uuid import UUID

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import Response
from fastapi import UploadFile
from fastapi import status

from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.receipt import ReceiptCreate
from app.schemas.receipt import ReceiptResponse
from app.schemas.receipt import ReceiptUpdate
from app.services.receipt_service import receipt_service
from app.utils.file_upload import save_receipt

router = APIRouter(
    prefix="/receipts",
    tags=["Receipts"],
)


# ---------------------------------------------------------
# Create Receipt
# ---------------------------------------------------------

@router.post(
    "/",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Receipt",
)
def create_receipt(
    receipt: ReceiptCreate,
    db: Session = Depends(get_db),
):

    return receipt_service.create_receipt(
        db,
        receipt,
    )


# ---------------------------------------------------------
# Get All Receipts
# ---------------------------------------------------------

@router.get(
    "/",
    response_model=list[ReceiptResponse],
    summary="Get Receipts",
)
def get_receipts(
    db: Session = Depends(get_db),
):

    return receipt_service.get_all(db)


# ---------------------------------------------------------
# Get Receipt By ID
# ---------------------------------------------------------

@router.get(
    "/{receipt_id}",
    response_model=ReceiptResponse,
    summary="Get Receipt By ID",
)
def get_receipt(
    receipt_id: UUID,
    db: Session = Depends(get_db),
):

    return receipt_service.get_by_id(
        db,
        receipt_id,
    )


# ---------------------------------------------------------
# Update Receipt
# ---------------------------------------------------------

@router.put(
    "/{receipt_id}",
    response_model=ReceiptResponse,
    summary="Update Receipt",
)
def update_receipt(
    receipt_id: UUID,
    receipt: ReceiptUpdate,
    db: Session = Depends(get_db),
):

    return receipt_service.update_receipt(
        db,
        receipt_id,
        receipt,
    )


# ---------------------------------------------------------
# Delete Receipt
# ---------------------------------------------------------

@router.delete(
    "/{receipt_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Receipt",
)
def delete_receipt(
    receipt_id: UUID,
    db: Session = Depends(get_db),
):

    receipt_service.delete_receipt(
        db,
        receipt_id,
    )

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )


# ---------------------------------------------------------
# Upload Receipt + OCR
# ---------------------------------------------------------

@router.post(
    "/upload",
    response_model=ReceiptResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Receipt",
)
async def upload_receipt(
    receipt_number: str = Form(...),
    expense_id: UUID = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    uploaded = await save_receipt(file)

    receipt = ReceiptCreate(
        receipt_number=receipt_number,
        expense_id=expense_id,
        original_filename=uploaded["original_filename"],
        stored_filename=uploaded["stored_filename"],
        file_path=uploaded["file_path"],
        file_type=uploaded["file_type"],
        file_size=uploaded["file_size"],
    )

    return receipt_service.upload_receipt(
        db,
        receipt,
    )