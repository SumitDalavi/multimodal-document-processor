import pytest
import os
import sys
import io
from unittest.mock import MagicMock, patch

# Mock dependencies
mock_fitz = MagicMock()
sys.modules["fitz"] = mock_fitz

mock_pil = MagicMock()
mock_image = MagicMock()
mock_pil.Image = mock_image
sys.modules["PIL"] = mock_pil

mock_tesseract = MagicMock()
sys.modules["pytesseract"] = mock_tesseract

mock_openai_module = MagicMock()
mock_openai_client = MagicMock()
mock_openai_module.OpenAI.return_value = mock_openai_client
sys.modules["openai"] = mock_openai_module

from fastapi.testclient import TestClient
from src.main import app, _check_ocr
import src.processor.extractor as extractor

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    # Reset globals for tests
    extractor._PYMUPDF = True
    extractor._OCR = True
    extractor._VISION = True

def test_health():
    res = client.get("/health")
    assert res.status_code == 200
    
    # Test _check_ocr success
    mock_tesseract.get_tesseract_version.return_value = "5.0.0"
    assert _check_ocr() is True
    
    # Test _check_ocr fail
    mock_tesseract.get_tesseract_version.side_effect = Exception("fail")
    assert _check_ocr() is False
    mock_tesseract.get_tesseract_version.side_effect = None

def test_process_invalid_type():
    res = client.post("/api/v1/process", files={"file": ("test.txt", b"txt", "text/plain")})
    assert res.status_code == 415

def test_process_too_large():
    import src.api.routes as routes
    routes.MAX_FILE_SIZE = 10
    res = client.post("/api/v1/process", files={"file": ("test.pdf", b"a"*20, "application/pdf")})
    assert res.status_code == 413
    routes.MAX_FILE_SIZE = 50 * 1024 * 1024

def test_process_pdf_no_pymupdf():
    extractor._PYMUPDF = False
    res = client.post("/api/v1/process", files={"file": ("test.pdf", b"pdf", "application/pdf")})
    assert res.status_code == 200
    assert "not installed" in res.json()["full_text"]

def test_process_pdf():
    # Mock fitz doc
    mock_doc = MagicMock()
    mock_page = MagicMock()
    mock_pix = MagicMock()
    mock_pix.tobytes.return_value = b"img"
    mock_page.get_pixmap.return_value = mock_pix
    
    # Emulate list-like len
    mock_doc.__len__.return_value = 1
    mock_doc.__getitem__.return_value = mock_page
    mock_fitz.open.return_value = mock_doc
    
    # Mock OCR
    mock_tesseract.image_to_string.return_value = "ocr text |table| \n chart"
    
    # Mock Vision JSON
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content='{"text": "vision", "tables": ["t"], "charts": ["c"], "has_tables": true}'))]
    mock_openai_client.chat.completions.create.return_value = mock_resp
    
    res = client.post("/api/v1/process", files={"file": ("test.pdf", b"pdf", "application/pdf")})
    assert res.status_code == 200
    data = res.json()
    assert data["total_pages"] == 1
    assert "ocr text" in data["full_text"] or "vision" in data["full_text"]
    
    # Test OCR error
    mock_tesseract.image_to_string.side_effect = Exception("err")
    res = client.post("/api/v1/process", data={"use_vision": False}, files={"file": ("test.pdf", b"pdf", "application/pdf")})
    assert "OCR error" in res.json()["full_text"]
    mock_tesseract.image_to_string.side_effect = None

    # Test OCR unavailable
    extractor._OCR = False
    res = client.post("/api/v1/process", data={"use_vision": False}, files={"file": ("test.pdf", b"pdf", "application/pdf")})
    assert "OCR unavailable" in res.json()["full_text"]
    extractor._OCR = True
    
    # Test vision JSON error
    mock_resp.choices = [MagicMock(message=MagicMock(content='bad json'))]
    res = client.post("/api/v1/process", files={"file": ("test.pdf", b"pdf", "application/pdf")})
    assert res.status_code == 200 # vision degrades gracefully

def test_process_image():
    # Mock OCR
    mock_tesseract.image_to_string.return_value = "ocr text"
    
    res = client.post("/api/v1/process", data={"use_vision": False}, files={"file": ("test.png", b"png", "image/png")})
    assert res.status_code == 200
    data = res.json()
    assert data["total_pages"] == 1
    assert "ocr text" in data["full_text"]

def test_process_unsupported_ext():
    # API allows PDF, PNG, JPG, WEBP but process() also checks ext.
    # So we force api to accept it to test the extractor
    import src.api.routes as routes
    routes.ALLOWED_TYPES.add("text/plain")
    res = client.post("/api/v1/process", files={"file": ("test.txt", b"txt", "text/plain")})
    assert res.status_code == 200
    assert "Unsupported file type" in res.json()["full_text"]

def test_process_text_only():
    mock_tesseract.image_to_string.return_value = "fast ocr"
    res = client.post("/api/v1/process/text", files={"file": ("test.png", b"png", "image/png")})
    assert res.status_code == 200
    assert "fast ocr" in res.json()["text"]
