from __future__ import annotations

import time

from .context_pipeline import ContextPipeline
from .redaction import redact_secrets
from .routing import ModelRouter
from .schemas import ChatRequest, ChatResponse, TokenUsage
from .telemetry import TelemetryCollector


class ModelGateway:
    def __init__(self, router: ModelRouter, context_pipeline: ContextPipeline, telemetry: TelemetryCollector) -> None:
        self.router = router
        self.context_pipeline = context_pipeline
        self.telemetry = telemetry

    def complete_chat(self, request: ChatRequest) -> ChatResponse:
        start = time.perf_counter()
        selected_model = self.router.choose(request)

        prompt = self.context_pipeline.build_prompt(request)
        prompt = redact_secrets(prompt)

        # MVP deterministic adapter placeholder; provider-specific adapters plug in here.
        answer = (
            f"[{selected_model.model_id}] intent={request.intent}: "
            "This is a scaffold response from the AI-AGENT model gateway."
        )

        latency_ms = int((time.perf_counter() - start) * 1000)
        usage = TokenUsage(
            prompt_tokens=max(1, len(prompt) // 4),
            completion_tokens=max(1, len(answer) // 4),
            total_tokens=max(1, len(prompt) // 4) + max(1, len(answer) // 4),
        )

        self.telemetry.emit(
            "chat_completion",
            {
                "model_id": selected_model.model_id,
                "intent": request.intent,
                "latency_ms": latency_ms,
            },
        )

        return ChatResponse(
            model=selected_model.model_id,
            content=answer,
            usage=usage,
            latency_ms=latency_ms,
        )
