import hashlib
from datetime import datetime

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Document
from app.schemas.document import DocumentResponse
from app.storage.s3 import S3Client


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/upload",
    response_model=DocumentResponse,
)
async def upload_document(
    file: UploadFile = File(...),
    policy_id: str = Form(...),
    document_name: str = Form(...),
    version: str = Form(...),
    effective_from: datetime = Form(...),
    effective_until: datetime | None = Form(None),
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Validate file
    # ---------------------------------------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported",
        )

    # ---------------------------------------------------------
    # Read file
    # ---------------------------------------------------------

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty",
        )

    # ---------------------------------------------------------
    # Calculate SHA-256
    # ---------------------------------------------------------

    file_hash = hashlib.sha256(
        file_content
    ).hexdigest()

    # ---------------------------------------------------------
    # Prevent duplicate upload
    # ---------------------------------------------------------

    existing_document = (
        db.query(Document)
        .filter(Document.file_hash == file_hash)
        .first()
    )

    if existing_document:
        raise HTTPException(
            status_code=409,
            detail="This document has already been uploaded",
        )

    # ---------------------------------------------------------
    # S3 key
    # ---------------------------------------------------------

    s3_key = (
        f"policies/"
        f"{policy_id}/"
        f"{version}/"
        f"{file.filename}"
    )

    # ---------------------------------------------------------
    # Upload to S3
    # ---------------------------------------------------------

    s3_client = S3Client()

    from io import BytesIO

    s3_client.upload_file(
        BytesIO(file_content),
        s3_key,
    )

    # ---------------------------------------------------------
    # Create database record
    # ---------------------------------------------------------

    document = Document(
        policy_id=policy_id,
        document_name=document_name,
        version=version,
        file_name=file.filename,
        file_hash=file_hash,
        s3_key=s3_key,
        status="UPLOADED",
        effective_from=effective_from,
        effective_until=effective_until,
        is_active=True,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document