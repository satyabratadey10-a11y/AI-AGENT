from __future__ import annotations

import httpx

from .base import ProviderAdapter
from ..schemas import ChatMessage

_DEFAULT_ENDPOINT = "https://api.anthropic.com"
_API_VERSION = "2023-06-01"
_DEFAULT_MAX_TOKENS = 4096


class AnthropicAdapter(ProviderAdapter):
    """Adapter for the Anthropic Messages API."""

    def __init__(self, endpoint: str = _DEFAULT_ENDPOINT, api_key: str | None = None) -> None:
        self._base = endpoint.rstrip("/")
        self._api_key = api_key

    async def complete(
        self,
        messages: list[ChatMessage],
        model_id: str,
        *,
        timeout: float = 30.0,
    ) -> str:
        headers: dict[str, str] = {
            "Content-Type": "application/json",
            "anthropic-version": _API_VERSION,
        }
        if self._api_key:
            headers["x-api-key"] = self._api_key

        # Anthropic keeps system messages separate from the messages array.
        system_parts = [m.content for m in messages if m.role == "system"]
        chat_messages = [
            {"role": m.role, "content": m.content}
            for m in messages
            if m.role != "system"
        ]

        payload: dict = {
            "model": model_id,
            "max_tokens": _DEFAULT_MAX_TOKENS,
            "messages": chat_messages,
        }
        if system_parts:
            payload["system"] = " ".join(system_parts)

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{self._base}/v1/messages",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        return data["content"][0]["text"]
