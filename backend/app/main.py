from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException, Response

from .context_pipeline import ContextPipeline
from .memory import ConversationMemory
from .model_gateway import ModelGateway
from .model_registry import ModelRegistry
from .routing import ModelRouter
from .schemas import (
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    HealthResponse,
    ModelRegistration,
    Project,
    ProjectCreate,
    ProviderRegistration,
    Workspace,
    WorkspaceCreate,
)
from .telemetry import TelemetryCollector

app = FastAPI(title="AI-AGENT Control Plane", version="0.1.0")

projects: dict[str, Project] = {}
workspaces: dict[str, Workspace] = {}

registry = ModelRegistry()
router = ModelRouter(registry)
telemetry = TelemetryCollector()
memory = ConversationMemory()
gateway = ModelGateway(router=router, context_pipeline=ContextPipeline(), telemetry=telemetry, registry=registry, memory=memory)


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse()


@app.get("/v1/projects", response_model=list[Project])
def list_projects() -> list[Project]:
    return list(projects.values())


@app.post("/v1/projects", response_model=Project)
def create_project(payload: ProjectCreate) -> Project:
    project = Project(id=str(uuid4()), name=payload.name, template=payload.template)
    projects[project.id] = project
    return project


@app.get("/v1/workspaces", response_model=list[Workspace])
def list_workspaces() -> list[Workspace]:
    return list(workspaces.values())


@app.post("/v1/workspaces", response_model=Workspace)
def create_workspace(payload: WorkspaceCreate) -> Workspace:
    if payload.project_id not in projects:
        raise HTTPException(status_code=404, detail="project not found")
    workspace = Workspace(id=str(uuid4()), project_id=payload.project_id, branch=payload.branch)
    workspaces[workspace.id] = workspace
    return workspace


@app.post("/v1/models/providers", response_model=ProviderRegistration)
def register_provider(payload: ProviderRegistration) -> ProviderRegistration:
    return registry.register_provider(payload)


@app.post("/v1/models", response_model=ModelRegistration)
def register_model(payload: ModelRegistration) -> ModelRegistration:
    try:
        return registry.register_model(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/v1/models", response_model=list[ModelRegistration])
def list_models() -> list[ModelRegistration]:
    return registry.list_models()


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(payload: ChatRequest) -> ChatResponse:
    try:
        return await gateway.complete_chat(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Conversation (memory) management
# ---------------------------------------------------------------------------

@app.post("/v1/conversations", response_model=ConversationHistory)
def create_conversation() -> ConversationHistory:
    """Create a new, empty conversation session and return its ID."""
    session_id = str(uuid4())
    return ConversationHistory(session_id=session_id, messages=[])


@app.get("/v1/conversations/{session_id}", response_model=ConversationHistory)
def get_conversation(session_id: str) -> ConversationHistory:
    """Return the full message history for a conversation."""
    return ConversationHistory(
        session_id=session_id,
        messages=memory.get_history(session_id),
    )


@app.delete("/v1/conversations/{session_id}")
def delete_conversation(session_id: str) -> Response:
    """Clear all history for a conversation session."""
    if not memory.clear(session_id):
        raise HTTPException(status_code=404, detail="conversation not found")
    return Response(status_code=204)
