"""
File Upload Utility

Author: Pravin Shanmugavel
Project: ExpenseIQ
"""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

UPLOAD_DIRECTORY = Path("uploads/receipts")
UPLOAD_DIRECTORY.mkdir(parents=True, exist_ok=True)


ALLOWED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".pdf",
}


async def save_receipt(
    file: UploadFile,
):

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            "Unsupported file format."
        )

    unique_name = (
        f"{uuid4().hex}{extension}"
    )

    destination = (
        UPLOAD_DIRECTORY / unique_name
    )

    contents = await file.read()

    with open(destination, "wb") as buffer:
        buffer.write(contents)

    await file.close()

    return {
        "original_filename": file.filename,
        "stored_filename": unique_name,
        "file_path": str(destination),
        "file_type": file.content_type,
        "file_size": destination.stat().st_size,
    }