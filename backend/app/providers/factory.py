from __future__ import annotations

from .base import ProviderAdapter
from .anthropic import AnthropicAdapter
from .gemini import GeminiAdapter
from .openai_compat import OpenAICompatAdapter
from ..schemas import ProviderRegistration


def build_adapter(registration: ProviderRegistration) -> ProviderAdapter:
    """Return the correct provider adapter for the given registration.

    Provider-type mapping:
    - ``openai``      → OpenAI-compatible (``/v1/chat/completions``)
    - ``openrouter``  → OpenRouter (OpenAI-compat, routed via openrouter.ai)
    - ``ollama``      → Ollama (OpenAI-compat, typically localhost:11434)
    - ``huggingface`` → HuggingFace serverless inference (OpenAI-compat endpoint)
    - ``custom``      → Any OpenAI-compatible self-hosted endpoint
    - ``anthropic``   → Anthropic Messages API
    - ``gemini``      → Google Gemini generateContent API
    """
    api_key = registration.api_key.get_secret_value() if registration.api_key else None
    endpoint = registration.endpoint

    if registration.provider_type == "anthropic":
        return AnthropicAdapter(endpoint=endpoint, api_key=api_key)
    if registration.provider_type == "gemini":
        return GeminiAdapter(endpoint=endpoint, api_key=api_key)
    # openai, openrouter, ollama, huggingface, custom all use the OpenAI-compat protocol.
    return OpenAICompatAdapter(endpoint=endpoint, api_key=api_key)
