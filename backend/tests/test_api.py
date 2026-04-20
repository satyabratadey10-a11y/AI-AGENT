from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_project_workspace_model_chat_flow() -> None:
    project_res = client.post("/v1/projects", json={"name": "demo", "template": "python"})
    assert project_res.status_code == 200
    project_id = project_res.json()["id"]

    workspace_res = client.post("/v1/workspaces", json={"project_id": project_id, "branch": "main"})
    assert workspace_res.status_code == 200

    provider_res = client.post(
        "/v1/models/providers",
        json={"provider_id": "self-hosted", "endpoint": "https://models.example.com", "auth_mode": "api_key"},
    )
    assert provider_res.status_code == 200

    model_res = client.post(
        "/v1/models",
        json={
            "model_id": "custom-code-1",
            "provider_id": "self-hosted",
            "capabilities": {
                "chat": True,
                "code_completion": True,
                "tool_calling": False,
                "context_window": 64000,
            },
            "latency_class": "balanced",
            "cost_class": "balanced",
            "safety_tier": "standard",
        },
    )
    assert model_res.status_code == 200

    chat_res = client.post(
        "/v1/chat/completions",
        json={
            "messages": [{"role": "user", "content": "Generate hello world"}],
            "intent": "generate",
            "preferred_model": "custom-code-1",
            "project_id": project_id,
            "open_files": ["main.py"],
        },
    )
    assert chat_res.status_code == 200
    chat_body = chat_res.json()
    assert chat_body["model"] == "custom-code-1"
    assert "scaffold response" in chat_body["content"]
