from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))
from main import app

client = TestClient(app)

def test_process_text_only():
    response = client.post("/process", json={"id": "doc1", "text": "This is a test document."})
    assert response.status_code == 200
    assert "summary" in response.json()
    assert "Processed document doc1" in response.json()["summary"]

def test_process_text_and_image():
    response = client.post("/process", json={"id": "doc2", "text": "Test", "image_url": "http://example.com/img.jpg"})
    assert response.status_code == 200
    assert "and an image" in response.json()["summary"]

def test_process_empty():
    response = client.post("/process", json={"id": "doc3"})
    assert response.status_code == 400
