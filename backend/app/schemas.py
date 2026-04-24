from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field, SecretStr


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
    timestamp: str = Field(default_factory=utc_now_iso)


class ProjectCreate(BaseModel):
    name: str
    template: str | None = None


class Project(BaseModel):
    id: str
    name: str
    template: str | None = None
    created_at: str = Field(default_factory=utc_now_iso)


class WorkspaceCreate(BaseModel):
    project_id: str
    branch: str = "main"


class Workspace(BaseModel):
    id: str
    project_id: str
    branch: str = "main"
    created_at: str = Field(default_factory=utc_now_iso)


class ProviderRegistration(BaseModel):
    provider_id: str
    endpoint: str
    auth_mode: Literal["none", "api_key", "oauth2"] = "api_key"
    provider_type: Literal["openai", "anthropic", "gemini", "ollama", "huggingface", "openrouter", "custom"] = "openai"
    api_key: SecretStr | None = None


class ModelCapabilities(BaseModel):
    chat: bool = True
    code_completion: bool = True
    tool_calling: bool = False
    context_window: int = 128000


class ModelRegistration(BaseModel):
    model_id: str
    provider_id: str
    capabilities: ModelCapabilities
    latency_class: Literal["low", "balanced", "high"] = "balanced"
    cost_class: Literal["low", "balanced", "high"] = "balanced"
    safety_tier: Literal["standard", "strict"] = "standard"


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    intent: Literal["explain", "generate", "refactor", "fix", "chat"] = "chat"
    preferred_model: str | None = None
    project_id: str | None = None
    open_files: list[str] = Field(default_factory=list)
    session_id: str | None = None  # omit to start a new conversation


class TokenUsage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatResponse(BaseModel):
    model: str
    content: str
    usage: TokenUsage
    latency_ms: int
    session_id: str  # always present so the client can continue the conversation


class ConversationHistory(BaseModel):
    session_id: str
    messages: list[ChatMessage]
