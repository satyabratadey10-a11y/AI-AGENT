from __future__ import annotations

from .model_registry import ModelRegistry
from .schemas import ChatRequest, ModelRegistration

_CODE_INTENTS = {"generate", "refactor", "fix"}
_CHAT_INTENTS = {"chat", "explain"}

_LATENCY_SCORE = {"low": 3, "balanced": 1, "high": 0}
_COST_SCORE = {"low": 2, "balanced": 1, "high": 0}


def _score_model(model: ModelRegistration, request: ChatRequest) -> int:
    score = 0
    if request.intent in _CODE_INTENTS and model.capabilities.code_completion:
        score += 10
    if request.intent in _CHAT_INTENTS and model.capabilities.chat:
        score += 10
    score += _LATENCY_SCORE.get(model.latency_class, 0)
    score += _COST_SCORE.get(model.cost_class, 0)
    return score


class ModelRouter:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def choose_with_fallbacks(self, request: ChatRequest) -> list[ModelRegistration]:
        """Return models in priority order for the request.

        The preferred model (if valid) is always first; remaining models are
        ranked by capability + latency/cost score so the gateway can fall back
        automatically when a provider is unavailable.
        """
        models = self.registry.list_models()
        if not models:
            raise ValueError("No models are registered")

        scored = sorted(models, key=lambda m: _score_model(m, request), reverse=True)

        preferred = None
        if request.preferred_model:
            preferred = self.registry.get_model(request.preferred_model)

        if preferred:
            result = [preferred] + [m for m in scored if m.model_id != preferred.model_id]
        else:
            result = scored

        return result

    def choose(self, request: ChatRequest) -> ModelRegistration:
        """Return the single best model for the request."""
        return self.choose_with_fallbacks(request)[0]
