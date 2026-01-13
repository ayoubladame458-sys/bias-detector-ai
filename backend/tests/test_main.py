"""
Basic tests for the API
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()
    assert response.json()["message"] == "BiasDetector API is running"


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_docs_available():
    """Test that API documentation is available"""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


# Add more tests for specific endpoints
@pytest.mark.asyncio
async def test_upload_invalid_file_type():
    """Test uploading file with invalid extension"""
    files = {"file": ("test.exe", b"fake content", "application/x-msdownload")}
    response = client.post("/api/v1/documents/upload", files=files)
    assert response.status_code == 400
    assert "not allowed" in response.json()["detail"].lower()
