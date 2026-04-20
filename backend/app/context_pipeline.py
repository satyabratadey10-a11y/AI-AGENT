from __future__ import annotations

from .schemas import ChatRequest


class ContextPipeline:
    """Minimal context shaping for MVP; can evolve to retrieval + diff-aware compression."""

    def build_prompt(self, request: ChatRequest) -> str:
        messages = [f"{m.role}: {m.content}" for m in request.messages]
        files = ", ".join(request.open_files) if request.open_files else "none"
        return "\n".join(
            [
                f"intent: {request.intent}",
                f"project_id: {request.project_id or 'n/a'}",
                f"open_files: {files}",
                *messages,
            ]
        )
