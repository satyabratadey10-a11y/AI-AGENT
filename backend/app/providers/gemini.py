from __future__ import annotations

import httpx

from .base import ProviderAdapter
from ..schemas import ChatMessage

_DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com"


class GeminiAdapter(ProviderAdapter):
    """Adapter for the Google Gemini generateContent API."""

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
        params: dict[str, str] = {}
        if self._api_key:
            params["key"] = self._api_key

        # Gemini uses "user"/"model" roles and a "contents" array.
        contents = []
        for m in messages:
            if m.role == "system":
                # Prepend system messages as a user turn so the model sees context.
                contents.append({"role": "user", "parts": [{"text": m.content}]})
            else:
                gemini_role = "model" if m.role == "assistant" else "user"
                contents.append({"role": gemini_role, "parts": [{"text": m.content}]})

        payload = {"contents": contents}
        url = f"{self._base}/v1beta/models/{model_id}:generateContent"

        async with httpx.AsyncClient(timeout=timeout) as client:
            resp = await client.post(url, json=payload, params=params)
            resp.raise_for_status()
            data = resp.json()

        return data["candidates"][0]["content"]["parts"][0]["text"]
