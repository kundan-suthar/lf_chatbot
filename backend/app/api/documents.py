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
from app.db.models import Document, DocumentChunk
from app.schemas.document import DocumentResponse
from app.storage.s3 import S3Client

from io import BytesIO
from pypdf import PdfReader
from app.services.llm.embeddings import EmbeddingClient
from app.ingestion.chunker import chunk_text

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


@router.post("/{document_id}/process")
def process_document(
    document_id: int,
    db: Session = Depends(get_db),
):
    # ---------------------------------------------------------
    # Find document
    # ---------------------------------------------------------

    document = db.get(Document, document_id)

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found",
        )

    # ---------------------------------------------------------
    # Prevent processing invalid states
    # ---------------------------------------------------------

    if document.status == "PROCESSING":
        raise HTTPException(
            status_code=409,
            detail="Document is already being processed",
        )

    # ---------------------------------------------------------
    # Mark processing
    # ---------------------------------------------------------

    document.status = "PROCESSING"
    db.commit()

    try:
        # -----------------------------------------------------
        # Download PDF from S3
        # -----------------------------------------------------

        s3 = S3Client()

        pdf_bytes = s3.download_file(
            document.s3_key
        )

        # -----------------------------------------------------
        # Extract text
        # -----------------------------------------------------

        reader = PdfReader(
            BytesIO(pdf_bytes)
        )

        pages = []

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                pages.append(page_text)

        full_text = "\n\n".join(pages)

        if not full_text.strip():
            raise ValueError(
                "No text could be extracted from PDF"
            )

        # -----------------------------------------------------
        # Chunk text
        # -----------------------------------------------------

        chunks = chunk_text(full_text)

        if not chunks:
            raise ValueError(
                "No chunks generated from document"
            )

        # -----------------------------------------------------
        # Generate embeddings
        # -----------------------------------------------------

        embedding_client = EmbeddingClient()

        # Remove existing chunks when re-processing
        db.query(DocumentChunk).filter(
            DocumentChunk.document_id == document.id
        ).delete()

        for index, content in enumerate(chunks):

            embedding = embedding_client.embed(
                content
            )

            chunk = DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=content,
                embedding=embedding,
                chunk_metadata={
                    "document_name": document.document_name,
                    "policy_id": document.policy_id,
                    "version": document.version,
                    "source": document.file_name,
                },
            )

            db.add(chunk)

        # -----------------------------------------------------
        # Mark document ready
        # -----------------------------------------------------

        document.status = "READY"

        db.commit()

        return {
            "document_id": document.id,
            "status": document.status,
            "chunks_created": len(chunks),
        }

    except Exception as exc:

        db.rollback()

        document.status = "FAILED"
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {str(exc)}",
        )
