from fastapi.testclient import TestClient


def test_health_check_endpoint(client: TestClient):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()

    assert data["status"] in ["healthy", "degraded"]
    assert data["app_name"] == "SourceIQ"
    assert "database" in data
    assert "latency_ms" in data["database"]
    assert "providers" in data
    assert data["providers"]["llm"] in ["gemini", "openai"]
    assert data["providers"]["embedding"] in ["gemini", "openai"]


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "SourceIQ"
    assert data["tagline"] == "AI Answers. Verifiable Sources."
