import uuid
from fastapi.testclient import TestClient


def test_create_and_get_workspace(client: TestClient):
    payload = {
        "name": "Research Group A",
        "description": "Comparative study documents",
    }
    create_res = client.post("/api/v1/workspaces/", json=payload)
    assert create_res.status_code == 201
    data = create_res.json()
    assert data["name"] == payload["name"]
    assert data["description"] == payload["description"]
    assert "id" in data
    workspace_id = data["id"]

    # Get by ID
    get_res = client.get(f"/api/v1/workspaces/{workspace_id}")
    assert get_res.status_code == 200
    get_data = get_res.json()
    assert get_data["id"] == workspace_id
    assert get_data["name"] == payload["name"]


def test_list_workspaces(client: TestClient):
    client.post("/api/v1/workspaces/", json={"name": "Workspace 1"})
    client.post("/api/v1/workspaces/", json={"name": "Workspace 2"})

    res = client.get("/api/v1/workspaces/")
    assert res.status_code == 200
    workspaces = res.json()
    assert isinstance(workspaces, list)
    assert len(workspaces) >= 2


def test_get_nonexistent_workspace_returns_404(client: TestClient):
    random_id = str(uuid.uuid4())
    res = client.get(f"/api/v1/workspaces/{random_id}")
    assert res.status_code == 404
    assert "detail" in res.json()


def test_delete_workspace(client: TestClient):
    create_res = client.post("/api/v1/workspaces/", json={"name": "To Delete"})
    workspace_id = create_res.json()["id"]

    delete_res = client.delete(f"/api/v1/workspaces/{workspace_id}")
    assert delete_res.status_code == 204

    # Verify gone
    get_res = client.get(f"/api/v1/workspaces/{workspace_id}")
    assert get_res.status_code == 404
