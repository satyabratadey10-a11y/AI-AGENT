from __future__ import annotations

from .model_registry import ModelRegistry
from .schemas import ChatRequest, ModelRegistration


class ModelRouter:
    def __init__(self, registry: ModelRegistry) -> None:
        self.registry = registry

    def choose(self, request: ChatRequest) -> ModelRegistration:
        if request.preferred_model:
            model = self.registry.get_model(request.preferred_model)
            if model:
                return model

        models = self.registry.list_models()
        if not models:
            raise ValueError("No models are registered")

        for model in models:
            if request.intent in {"generate", "refactor", "fix"} and model.capabilities.code_completion:
                return model
            if request.intent in {"chat", "explain"} and model.capabilities.chat:
                return model

        return models[0]
