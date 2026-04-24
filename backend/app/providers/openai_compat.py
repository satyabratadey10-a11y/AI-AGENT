from __future__ import annotations

import httpx

from .base import ProviderAdapter
from ..schemas import ChatMessage


class OpenAICompatAdapter(ProviderAdapter):
    """Adapter for the OpenAI chat-completions API protocol.

    Compatible providers: OpenAI, OpenRouter, Ollama (/v1/chat/completions),
    HuggingFace serverless inference, Mistral AI, and any custom endpoint
    that implements the same protocol.
    """

    def __init__(self, endpoint: str, api_key: str | None = None) -> None:
        self._base = endpoint.rstrip("/")
        self._api_key = api_key

    async def complete(
        self,
        messages: list[ChatMessage],
        model_id: str,
        *,
        timeout: float = 30.0,
    ) -> str:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload = {
            "model": model_id,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
        }

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(
                f"{self._base}/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            resp.raise_for_status()
            data = resp.json()

        return data["choices"][0]["message"]["content"]
