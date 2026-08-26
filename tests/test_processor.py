"""Tests for the multimodal document processor."""
import io
import pytest
from unittest.mock import patch, MagicMock

from src.processor.models import ContentType, ExtractedBlock, PageResult, DocumentResult
from src.processor.extractor import extract_document, _heuristic_detection


# ── Model Tests ───────────────────────────────────────────────────────────────

def test_extracted_block_content_types():
    for ct in ContentType:
        block = ExtractedBlock(
            block_id="test-id", page=1, content_type=ct,
            text="test", confidence=0.9,
        )
        assert block.content_type == ct


def test_document_result_defaults():
    result = DocumentResult(
        document_id="abc", filename="test.pdf", total_pages=3,
    )
    assert result.pages == []
    assert result.status == "processed"
    assert result.processing_time_ms == 0.0


# ── Extractor Tests ───────────────────────────────────────────────────────────

def test_extract_unsupported_extension():
    """Unsupported file types should return an error block rather than crash."""
    result = extract_document(b"data", "doc.xyz")
    assert result.total_pages == 1
    assert "Unsupported" in result.full_text


def test_extract_image_without_ocr(monkeypatch):
    """Without tesseract, should degrade gracefully with an informative message."""
    monkeypatch.setattr("src.processor.extractor._OCR", False)
    monkeypatch.setattr("src.processor.extractor._VISION", False)

    # Create a minimal valid PNG (1x1 white pixel)
    import struct, zlib
    def mk_png():
        def chunk(name, data):
            c = struct.pack(">I", len(data)) + name + data
            c += struct.pack(">I", zlib.crc32(name + data) & 0xffffffff)
            return c
        raw = (b"\x89PNG\r\n\x1a\n" +
               chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)) +
               chunk(b"IDAT", zlib.compress(b"\x00\xff\xff\xff")) +
               chunk(b"IEND", b""))
        return raw

    result = extract_document(mk_png(), "test.png", use_vision=False)
    assert result.total_pages == 1
    assert result.filename == "test.png"
    assert result.document_id != ""


# ── API Tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint():
    from fastapi.testclient import TestClient
    from src.main import app
    client = TestClient(app)
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "ocr_available" in data
    assert "vision_available" in data


@pytest.mark.asyncio
async def test_process_unsupported_type():
    from fastapi.testclient import TestClient
    from src.main import app
    client = TestClient(app)
    resp = client.post(
        "/api/v1/process",
        files={"file": ("test.txt", b"hello world", "text/plain")},
        data={"use_vision": "false"},
    )
    assert resp.status_code == 415
