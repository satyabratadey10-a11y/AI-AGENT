from __future__ import annotations

from abc import ABC, abstractmethod

from ..schemas import ChatMessage


class ProviderAdapter(ABC):
    """Abstract interface every provider adapter must implement."""

    @abstractmethod
    async def complete(
        self,
        messages: list[ChatMessage],
        model_id: str,
        *,
        timeout: float = 30.0,
    ) -> str: ...
