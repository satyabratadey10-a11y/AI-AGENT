from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from .schemas import ModelRegistration, ProviderRegistration


@dataclass
class RegistryState:
    providers: Dict[str, ProviderRegistration]
    models: Dict[str, ModelRegistration]


class ModelRegistry:
    def __init__(self) -> None:
        self._state = RegistryState(providers={}, models={})

    def register_provider(self, provider: ProviderRegistration) -> ProviderRegistration:
        self._state.providers[provider.provider_id] = provider
        return provider

    def register_model(self, model: ModelRegistration) -> ModelRegistration:
        if model.provider_id not in self._state.providers:
            raise ValueError(f"Unknown provider_id: {model.provider_id}")
        self._state.models[model.model_id] = model
        return model

    def list_models(self) -> list[ModelRegistration]:
        return list(self._state.models.values())

    def get_model(self, model_id: str) -> ModelRegistration | None:
        return self._state.models.get(model_id)

    def get_provider(self, provider_id: str) -> ProviderRegistration | None:
        return self._state.providers.get(provider_id)

    def has_models(self) -> bool:
        return bool(self._state.models)
