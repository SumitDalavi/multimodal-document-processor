import pytest
from fastapi.testclient import TestClient
from src.main import app
import io

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_process_document_pdf():
    file_content = b"%PDF-1.4 mock pdf content"
    response = client.post(
        "/api/v1/process",
        files={"file": ("test.pdf", io.BytesIO(file_content), "application/pdf")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.pdf"
    assert data["status"] == "processed"
    assert "PDF document" in data["ocr_text_preview"]

def test_process_document_image():
    file_content = b"fake image bytes"
    response = client.post(
        "/api/v1/process",
        files={"file": ("test.png", io.BytesIO(file_content), "image/png")}
    )
    assert response.status_code == 200
    assert "extracted from Image" in response.json()["ocr_text_preview"]
