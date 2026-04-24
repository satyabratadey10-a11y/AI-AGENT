from __future__ import annotations

import asyncio
import time
from uuid import uuid4

import httpx

from .context_pipeline import ContextPipeline
from .memory import ConversationMemory
from .model_registry import ModelRegistry
from .providers import ProviderAdapter, build_adapter
from .redaction import redact_secrets
from .routing import ModelRouter
from .schemas import ChatMessage, ChatRequest, ChatResponse, TokenUsage
from .telemetry import TelemetryCollector

_MAX_RETRIES = 2
_RETRY_STATUSES = {429, 500, 502, 503, 504}


class ModelGateway:
    def __init__(
        self,
        router: ModelRouter,
        context_pipeline: ContextPipeline,
        telemetry: TelemetryCollector,
        registry: ModelRegistry,
        memory: ConversationMemory,
    ) -> None:
        self.router = router
        self.context_pipeline = context_pipeline
        self.telemetry = telemetry
        self.registry = registry
        self.memory = memory
        self._adapters: dict[str, ProviderAdapter] = {}

    def _get_adapter(self, provider_id: str) -> ProviderAdapter:
        if provider_id not in self._adapters:
            provider = self.registry.get_provider(provider_id)
            if provider is None:
                raise ValueError(f"Provider not registered: {provider_id}")
            self._adapters[provider_id] = build_adapter(provider)
        return self._adapters[provider_id]

    async def _call_with_retry(
        self,
        adapter: ProviderAdapter,
        request: ChatRequest,
        model_id: str,
        *,
        timeout: float = 30.0,
    ) -> str:
        last_exc: Exception | None = None
        for attempt in range(_MAX_RETRIES + 1):
            try:
                return await adapter.complete(request.messages, model_id, timeout=timeout)
            except httpx.HTTPStatusError as exc:
                if exc.response.status_code not in _RETRY_STATUSES or attempt == _MAX_RETRIES:
                    raise
                last_exc = exc
                await asyncio.sleep(2**attempt)
            except (httpx.ConnectError, httpx.TimeoutException) as exc:
                if attempt == _MAX_RETRIES:
                    raise
                last_exc = exc
                await asyncio.sleep(2**attempt)
        assert last_exc is not None  # loop only reaches here after at least one caught exception
        raise last_exc

    async def complete_chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()

        # Resolve or create the session.
        session_id = request.session_id or str(uuid4())

        # Prepend stored history so the model sees the full conversation.
        history = self.memory.get_history(session_id)
        messages_with_history = history + request.messages

        # Build prompt for token-counting / telemetry (uses the full message list).
        enriched = request.model_copy(update={"messages": messages_with_history})
        prompt = self.context_pipeline.build_prompt(enriched)
        prompt = redact_secrets(prompt)

        candidates = self.router.choose_with_fallbacks(request)

        answer: str | None = None
        selected_model_id = candidates[0].model_id
        last_exc: Exception | None = None

        for model in candidates:
            try:
                adapter = self._get_adapter(model.provider_id)
                answer = await self._call_with_retry(adapter, enriched, model.model_id)
                selected_model_id = model.model_id
                break
            except (httpx.HTTPError, ValueError, KeyError, IndexError) as exc:
                # Provider call failed; try the next candidate in the fallback list.
                last_exc = exc
                continue

        if answer is None:
            attempted = len(candidates)
            failed_ids = ", ".join(m.model_id for m in candidates)
            raise ValueError(
                f"All {attempted} provider adapter(s) failed (tried: {failed_ids}). "
                f"Last error: {last_exc}"
            ) from last_exc

        # Persist this turn: new user messages + assistant reply.
        turn: list[ChatMessage] = request.messages + [
            ChatMessage(role="assistant", content=answer)
        ]
        self.memory.append_turn(session_id, turn)

        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = TokenUsage(
            prompt_tokens=max(1, len(prompt) // 4),
            completion_tokens=max(1, len(answer) // 4),
            total_tokens=max(1, len(prompt) // 4) + max(1, len(answer) // 4),
        )

        self.telemetry.emit(
            "chat_completion",
            {
                "model_id": selected_model_id,
                "intent": request.intent,
                "latency_ms": latency_ms,
                "session_id": session_id,
            },
        )

        return ChatResponse(
            model=selected_model_id,
            content=answer,
            usage=usage,
            latency_ms=latency_ms,
            session_id=session_id,
        )
