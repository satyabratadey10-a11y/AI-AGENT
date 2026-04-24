from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.main import app, memory
from app.schemas import ChatResponse, TokenUsage


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

    mock_response = ChatResponse(
        model="custom-code-1",
        content="print('Hello, world!')",
        usage=TokenUsage(prompt_tokens=10, completion_tokens=20, total_tokens=30),
        latency_ms=50,
        session_id="test-session-id",
    )
    with patch("app.main.gateway.complete_chat", new_callable=AsyncMock, return_value=mock_response):
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
    assert "Hello" in chat_body["content"]
    assert chat_body["session_id"] == "test-session-id"


def test_conversation_create_get_delete() -> None:
    # Create
    res = client.post("/v1/conversations")
    assert res.status_code == 200
    body = res.json()
    session_id = body["session_id"]
    assert session_id
    assert body["messages"] == []

    # GET returns empty history (no chats yet in this test)
    get_res = client.get(f"/v1/conversations/{session_id}")
    assert get_res.status_code == 200
    assert get_res.json()["session_id"] == session_id

    # Seed memory directly to verify GET returns it
    from app.schemas import ChatMessage as CM
    memory.append_turn(session_id, [CM(role="user", content="test")])
    get_res2 = client.get(f"/v1/conversations/{session_id}")
    assert len(get_res2.json()["messages"]) == 1

    # DELETE clears the session
    del_res = client.delete(f"/v1/conversations/{session_id}")
    assert del_res.status_code == 204

    # Second DELETE → 404
    del_res2 = client.delete(f"/v1/conversations/{session_id}")
    assert del_res2.status_code == 404
