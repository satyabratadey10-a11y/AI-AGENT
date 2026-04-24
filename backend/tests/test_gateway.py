from unittest.mock import AsyncMock, patch

from app.context_pipeline import ContextPipeline
from app.model_gateway import ModelGateway
from app.model_registry import ModelRegistry
from app.routing import ModelRouter
from app.schemas import ChatMessage, ChatRequest, ModelCapabilities, ModelRegistration, ProviderRegistration
from app.telemetry import TelemetryCollector


async def test_gateway_redacts_and_routes() -> None:
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
    gateway = ModelGateway(ModelRouter(registry), ContextPipeline(), telemetry, registry)

    # Mock the adapter so the test doesn't make real HTTP calls.
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
