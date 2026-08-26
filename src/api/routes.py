"""FastAPI routes for document processing."""
from __future__ import annotations
import os
import uuid
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from src.processor.extractor import extract_document
from src.processor.models import DocumentResult

router = APIRouter(prefix="/api/v1", tags=["documents"])

MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "50")) * 1024 * 1024
ALLOWED_TYPES = {"application/pdf", "image/png", "image/jpeg", "image/webp"}


@router.post("/process", response_model=DocumentResult, summary="Process a document")
async def process_document(
    file: UploadFile = File(..., description="PDF or image file to process"),
    use_vision: bool = Form(True, description="Use GPT-4o vision for chart/table analysis"),
):
    """
    Upload a document (PDF or image) and extract all content including:
    - Plain text (via OCR)
    - Tables (as Markdown)
    - Charts and graphs (described via vision LLM)
    - Figures and diagrams
    """
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {ALLOWED_TYPES}",
        )

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_FILE_SIZE // 1024 // 1024} MB",
        )

    doc_id = str(uuid.uuid4())
    result = extract_document(
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        document_id=doc_id,
        use_vision=use_vision,
    )
    return result


@router.post("/process/text", summary="Extract text only (fast mode)")
async def process_text_only(file: UploadFile = File(...)):
    """Fast extraction using OCR only — no vision LLM calls."""
    file_bytes = await file.read()
    result = extract_document(
        file_bytes=file_bytes,
        filename=file.filename or "unknown",
        use_vision=False,
    )
    return {"document_id": result.document_id, "text": result.full_text, "pages": result.total_pages}
