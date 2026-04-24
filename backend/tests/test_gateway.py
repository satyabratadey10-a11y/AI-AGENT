from unittest.mock import AsyncMock, patch

from app.context_pipeline import ContextPipeline
from app.memory import ConversationMemory
from app.model_gateway import ModelGateway
from app.model_registry import ModelRegistry
from app.routing import ModelRouter
from app.schemas import ChatMessage, ChatRequest, ModelCapabilities, ModelRegistration, ProviderRegistration
from app.telemetry import TelemetryCollector


def _make_gateway() -> tuple[ModelGateway, ModelRegistry, TelemetryCollector, ConversationMemory]:
    registry = ModelRegistry()
    registry.register_provider(
        ProviderRegistration(
            provider_id="p1",
            endpoint="https://example.com",
            auth_mode="api_key",
            provider_type="openai",
        )
    )
    registry.register_model(
        ModelRegistration(
            model_id="m1",
            provider_id="p1",
            capabilities=ModelCapabilities(chat=True, code_completion=True, tool_calling=False, context_window=16000),
            latency_class="low",
            cost_class="low",
            safety_tier="standard",
        )
    )
    telemetry = TelemetryCollector()
    memory = ConversationMemory()
    gateway = ModelGateway(ModelRouter(registry), ContextPipeline(), telemetry, registry, memory)
    return gateway, registry, telemetry, memory


async def test_gateway_redacts_and_routes() -> None:
    gateway, _registry, telemetry, _memory = _make_gateway()

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = AsyncMock(return_value="Hello from m1!")
        mock_get_adapter.return_value = mock_adapter

        response = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="my api_key=secret12345")],
                intent="chat",
                preferred_model="m1",
                project_id="p",
                open_files=[],
            )
        )

    assert response.model == "m1"
    assert response.usage.total_tokens >= 1
    assert telemetry.events and telemetry.events[0].event_name == "chat_completion"
    assert response.session_id  # a session_id must always be returned


async def test_memory_accumulates_across_turns() -> None:
    """Subsequent turns within the same session include prior history."""
    gateway, _registry, _telemetry, memory = _make_gateway()

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = AsyncMock(return_value="Turn 1 reply")
        mock_get_adapter.return_value = mock_adapter

        r1 = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Hello")],
                intent="chat",
                preferred_model="m1",
            )
        )

    session_id = r1.session_id
    history_after_turn1 = memory.get_history(session_id)
    assert len(history_after_turn1) == 2  # user + assistant
    assert history_after_turn1[0].role == "user"
    assert history_after_turn1[1].role == "assistant"
    assert history_after_turn1[1].content == "Turn 1 reply"

    # Second turn — history must be prepended to the outgoing messages.
    captured_messages: list = []

    async def capture_complete(messages: list[ChatMessage], model_id: str, *, timeout: float = 30.0) -> str:
        captured_messages.extend(messages)
        return "Turn 2 reply"

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = capture_complete
        mock_get_adapter.return_value = mock_adapter

        r2 = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Follow-up")],
                intent="chat",
                preferred_model="m1",
                session_id=session_id,
            )
        )

    assert r2.session_id == session_id
    # The adapter received: history (user + assistant) + new user message = 3
    assert len(captured_messages) == 3
    assert captured_messages[0].content == "Hello"
    assert captured_messages[1].content == "Turn 1 reply"
    assert captured_messages[2].content == "Follow-up"

    # Memory now has 4 messages total.
    assert len(memory.get_history(session_id)) == 4


async def test_new_session_created_without_session_id() -> None:
    gateway, _registry, _telemetry, memory = _make_gateway()

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = AsyncMock(return_value="Reply")
        mock_get_adapter.return_value = mock_adapter

        r = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Hi")],
                intent="chat",
                preferred_model="m1",
            )
        )

    assert r.session_id
    assert r.session_id in memory.list_sessions()


async def test_session_isolation() -> None:
    """Two different sessions must not share history."""
    gateway, _registry, _telemetry, memory = _make_gateway()

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = AsyncMock(return_value="Reply A")
        mock_get_adapter.return_value = mock_adapter

        ra = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Session A message")],
                intent="chat",
                preferred_model="m1",
            )
        )

    with patch.object(gateway, "_get_adapter") as mock_get_adapter:
        mock_adapter = AsyncMock()
        mock_adapter.complete = AsyncMock(return_value="Reply B")
        mock_get_adapter.return_value = mock_adapter

        rb = await gateway.complete_chat(
            ChatRequest(
                messages=[ChatMessage(role="user", content="Session B message")],
                intent="chat",
                preferred_model="m1",
            )
        )

    assert ra.session_id != rb.session_id
    hist_a = memory.get_history(ra.session_id)
    hist_b = memory.get_history(rb.session_id)
    assert all(m.content != "Session B message" for m in hist_a)
    assert all(m.content != "Session A message" for m in hist_b)
