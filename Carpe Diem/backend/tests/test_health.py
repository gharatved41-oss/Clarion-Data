"""Tests for health check and core application behavior."""
from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Test GET /health returns 200 OK and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_404_not_found(client: TestClient):
    """Test requesting a non-existent endpoint returns standard 404 JSON."""
    response = client.get("/non-existent-path")
    assert response.status_code == 404
    data = response.json()
    assert data.get("error") == "HTTPException"
    assert data.get("status_code") == 404


def test_cors_headers(client: TestClient):
    """Test CORS headers are present on options preflight request."""
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET"
        }
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"

