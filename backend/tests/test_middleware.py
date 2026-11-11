from fastapi.testclient import TestClient


def test_security_headers_and_timing(client: TestClient):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    
    headers = response.headers
    assert "X-Request-ID" in headers
    assert "X-Process-Time" in headers
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "default-src 'self'" in headers["Content-Security-Policy"]
