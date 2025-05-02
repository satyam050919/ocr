import io
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert "docs_url" in response.json()
    assert "redoc_url" in response.json()


def test_process_document_invalid_file_type():
    response = client.post(
        "/documents/process",
        files={"file": ("test.txt", io.BytesIO(b"test content"), "text/plain")},
        data={"auto_detect_type": "true"}
    )
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
