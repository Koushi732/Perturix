from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "ok"

def test_system_info(client: TestClient):
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    data = response.json()["data"]
    assert "app_name" in data
    assert "environment" in data

def test_system_status(client: TestClient):
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["status"] == "operational"
