from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI, HTTPException

from .context_pipeline import ContextPipeline
from .model_gateway import ModelGateway
from .model_registry import ModelRegistry
from .routing import ModelRouter
from .schemas import (
    ChatRequest,
    ChatResponse,
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
gateway = ModelGateway(router=router, context_pipeline=ContextPipeline(), telemetry=telemetry)


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
def chat_completions(payload: ChatRequest) -> ChatResponse:
    try:
        return gateway.complete_chat(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
