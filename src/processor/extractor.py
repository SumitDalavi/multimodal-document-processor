"""
Core document extraction engine.
Handles PDF-to-image conversion, OCR, table detection, and
optional vision LLM analysis for charts and complex layouts.
"""
from __future__ import annotations
import io
import os
import re
import time
import uuid
import base64
from typing import List, Optional, Tuple

from src.processor.models import (
    ContentType, ExtractedBlock, PageResult, DocumentResult
)

# ── Optional imports (degrade gracefully if not installed) ────────────────────
try:
    import fitz  # PyMuPDF
    _PYMUPDF = True
except ImportError:
    _PYMUPDF = False

try:
    from PIL import Image
    import pytesseract
    _OCR = True
    tesseract_cmd = os.getenv("TESSERACT_CMD")
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
except ImportError:
    _OCR = False

try:
    from openai import OpenAI
    _vision_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
    _VISION = bool(os.getenv("OPENAI_API_KEY"))
except Exception:
    _VISION = False


def extract_document(
    file_bytes: bytes,
    filename: str,
    document_id: Optional[str] = None,
    use_vision: bool = True,
) -> DocumentResult:
    """
    Main entry point. Accepts raw file bytes and returns a DocumentResult.
    Supports: PDF, PNG, JPG, JPEG.
    """
    if document_id is None:
        document_id = str(uuid.uuid4())

    start = time.time()
    ext = filename.lower().split(".")[-1]

    if ext == "pdf":
        pages = _process_pdf(file_bytes, use_vision=use_vision and _VISION)
    elif ext in ("png", "jpg", "jpeg", "webp"):
        pages = _process_image(file_bytes, filename, use_vision=use_vision and _VISION)
    else:
        pages = [PageResult(
            page_number=1,
            raw_text=f"Unsupported file type: {ext}",
            blocks=[ExtractedBlock(
                block_id=str(uuid.uuid4()),
                page=1,
                content_type=ContentType.TEXT,
                text=f"Unsupported file type: {ext}",
                confidence=0.0,
            )],
        )]

    full_text = "\n\n".join(p.raw_text for p in pages)
    images_count = sum(1 for p in pages if p.has_images)
    elapsed = (time.time() - start) * 1000

    return DocumentResult(
        document_id=document_id,
        filename=filename,
        total_pages=len(pages),
        pages=pages,
        full_text=full_text,
        images_count=images_count,
        processing_time_ms=round(elapsed, 2),
        model_used="gpt-4o" if (use_vision and _VISION) else ("tesseract" if _OCR else "heuristic"),
    )


def _process_pdf(pdf_bytes: bytes, use_vision: bool) -> List[PageResult]:
    """Convert PDF pages to images then extract content from each."""
    pages = []
    if not _PYMUPDF:
        return [PageResult(
            page_number=1,
            raw_text="[PyMuPDF not installed. Install with: pip install pymupdf]",
        )]

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    for page_num in range(len(doc)):
        page = doc[page_num]
        # Render at 150 DPI for good OCR quality without being too slow
        mat = fitz.Matrix(150/72, 150/72)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")

        page_result = _extract_from_image_bytes(
            img_bytes, page_num + 1, use_vision
        )
        pages.append(page_result)
    doc.close()
    return pages


def _process_image(img_bytes: bytes, filename: str, use_vision: bool) -> List[PageResult]:
    """Extract content from a single image file."""
    page = _extract_from_image_bytes(img_bytes, 1, use_vision)
    return [page]


def _extract_from_image_bytes(
    img_bytes: bytes, page_num: int, use_vision: bool
) -> PageResult:
    """Extract all content blocks from an image (page render or standalone image)."""
    blocks: List[ExtractedBlock] = []
    raw_text = ""

    # ── OCR: extract text ─────────────────────────────────────────────────────
    if _OCR:
        try:
            img = Image.open(io.BytesIO(img_bytes))
            ocr_text = pytesseract.image_to_string(img, config="--psm 3")
            raw_text = ocr_text.strip()
            if raw_text:
                blocks.append(ExtractedBlock(
                    block_id=str(uuid.uuid4()),
                    page=page_num,
                    content_type=ContentType.TEXT,
                    text=raw_text,
                    confidence=0.85,
                ))
        except Exception as e:
            raw_text = f"[OCR error: {e}]"
    else:
        raw_text = "[OCR unavailable — install pytesseract + tesseract-ocr]"
        blocks.append(ExtractedBlock(
            block_id=str(uuid.uuid4()),
            page=page_num,
            content_type=ContentType.TEXT,
            text=raw_text,
            confidence=0.0,
        ))

    # ── Vision LLM: analyse charts, tables, complex layouts ──────────────────
    has_charts = False
    has_tables = False
    has_images = False

    if use_vision and _VISION:
        vision_result = _analyze_with_vision(img_bytes, page_num)
        if vision_result:
            blocks.extend(vision_result["blocks"])
            has_charts = vision_result.get("has_charts", False)
            has_tables = vision_result.get("has_tables", False)
            has_images = vision_result.get("has_images", False)
            # Prefer vision-extracted text if OCR was weak
            if not raw_text or len(raw_text) < 50:
                vision_text = "\n".join(
                    b.text for b in vision_result["blocks"]
                    if b.content_type == ContentType.TEXT
                )
                raw_text = vision_text or raw_text
    else:
        # Heuristic detection from OCR text
        lower = raw_text.lower()
        has_tables = bool(re.search(r"(\|.+\|)|(\t.+\t)", raw_text))
        has_charts = any(w in lower for w in ["figure", "chart", "graph", "plot"])
        has_images = any(w in lower for w in ["image", "photo", "diagram"])

    return PageResult(
        page_number=page_num,
        blocks=blocks,
        raw_text=raw_text,
        has_images=has_images,
        has_tables=has_tables,
        has_charts=has_charts,
    )


def _analyze_with_vision(img_bytes: bytes, page_num: int) -> Optional[dict]:
    """Use GPT-4o vision to deeply analyse a page image."""
    try:
        b64 = base64.b64encode(img_bytes).decode()
        response = _vision_client.chat.completions.create(
            model="gpt-4o",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Analyse this document page. Extract ALL content:\n"
                            "1. Full text (verbatim)\n"
                            "2. Any tables (as Markdown)\n"
                            "3. Any charts/graphs (describe data, axes, trends)\n"
                            "4. Any diagrams (describe components and relationships)\n"
                            "Format as JSON: {\"text\": \"...\", \"tables\": [\"...\"], "
                            "\"charts\": [\"...\"], \"has_tables\": bool, "
                            "\"has_charts\": bool, \"has_images\": bool}"
                        ),
                    },
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                ],
            }],
            max_tokens=2000,
        )
        import json
        raw = response.choices[0].message.content
        # Extract JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if not match:
            return None
        data = json.loads(match.group())

        result_blocks = []
        if data.get("text"):
            result_blocks.append(ExtractedBlock(
                block_id=str(uuid.uuid4()), page=page_num,
                content_type=ContentType.TEXT, text=data["text"], confidence=0.95,
            ))
        for tbl in data.get("tables", []):
            result_blocks.append(ExtractedBlock(
                block_id=str(uuid.uuid4()), page=page_num,
                content_type=ContentType.TABLE, text=tbl, confidence=0.90,
            ))
        for chart in data.get("charts", []):
            result_blocks.append(ExtractedBlock(
                block_id=str(uuid.uuid4()), page=page_num,
                content_type=ContentType.CHART, text=chart, confidence=0.85,
            ))

        return {
            "blocks": result_blocks,
            "has_tables": data.get("has_tables", False),
            "has_charts": data.get("has_charts", False),
            "has_images": data.get("has_images", False),
        }
    except Exception as e:
        return None
